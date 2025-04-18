import csv
import json
import collections
import uuid
import logging
from cltk.languages.utils import get_lang
import pathlib

# import lmp.utils as u
import utils as u
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def build_db(iso_glotto_fname, ethnologue_fname,
			written_status_fname,
			wals_dirpath, grambank_dirpath,
			output_dir):

	parameters = {"WALS": collections.defaultdict(lambda: set()),
				"GRAMBANK": collections.defaultdict(lambda: set())}

	#MAP
	reader = csv.DictReader(open(iso_glotto_fname, encoding="utf-8"), delimiter=",", quotechar='"')
	glottocodes = []
	isoglottomap = {}
	glottoisomap = {}
	for line in reader:
		if len(line["ISO639P3code"].strip())>0:
			isoglottomap[line["ISO639P3code"]] = line
			glottoisomap[line["ID"]] = line
		glottocodes.append(line["ID"])

	logging.info(f"Reading ISO Glotto data, {len(isoglottomap)} items found")

	#ETHNOLOGUE
	ethnologue = u.read_csv(ethnologue_fname, key="ISO 639")
	written_data = u.read_csv(written_status_fname, key="ISO 639")
	for lang_id, lang in ethnologue.items():
		lang["Written"] = written_data[lang_id]["status"]

	logging.info(f"Reading Ethnologue data, {len(ethnologue)} items found")

	#WALS
	wals_languages = u.read_csv(wals_dirpath.joinpath("languages.csv"), "ID")
	wals_parameters = u.read_csv(wals_dirpath.joinpath("parameters.csv"), "ID")
	wals_codes = u.read_csv(wals_dirpath.joinpath("codes.csv"), "ID")
	wals_values = u.read_csv(wals_dirpath.joinpath("values.csv"), "ID")
	wals_tosave = {}

	logging.info(f"Reading WALS data, {len(wals_languages)} items found")
	logging.info(f"Reading WALS data, {len(wals_parameters)} parameters found")


	for element_id, element in wals_values.items():
		language = element["Language_ID"]
		if not language in wals_tosave:
			wals_tosave[language] = {"Glottocode": wals_languages[language]["Glottocode"],
									"ID": wals_languages[language]["ID"]}
		parameter = element["Parameter_ID"]
		value = element["Value"]
		# wals_languages[language][f"PARAM:{wals_parameters[parameter]['Name']}"] = wals_codes[f"{parameter}-{value}"]["Description"]
		wals_tosave[language][f"W:{wals_parameters[parameter]['Name']}"] = wals_codes[f"{parameter}-{value}"]["Description"]

		parameters["WALS"][f"{wals_parameters[parameter]['Name']}"].add(wals_codes[f"{parameter}-{value}"]["Description"])

	glotto_wals = {}
	noglotto_wals = []
	for language_id, language in wals_tosave.items():
		if len(language["Glottocode"]) > 0:
			if not language["Glottocode"] in glotto_wals:
				glotto_wals[language["Glottocode"]] = []
			glotto_wals[language["Glottocode"]].append(language)
		else:
			noglotto_wals.append(language)

	logging.info(f"Among WALS languages, {len(wals_languages)-len(noglotto_wals)} have glottocode and {len(noglotto_wals)} do not")
	logging.info(f"Total number of ISO codes found in WALS: {len(glotto_wals)}")

	logging.info(f"Number of languages with more than one isocode per glottocode: {len([x for x in glotto_wals if len(glotto_wals[x]) > 1])}")


	# TODO: if all missing merge, otherwise signal differences.
	with open(output_dir.joinpath("prova_glottowals.txt"), "w") as fout:
		for language in glotto_wals:

			if len(glotto_wals[language]) > 1:
				tmp = [(subl["ID"], len(subl)-2) for subl in glotto_wals[language]]
				print(f"{language}: {tmp}", file=fout)
				logging.warning(f"Glottocode {language} has more than one WALS language:")
				for sublanguage in glotto_wals[language]:
					print(f"\t{sublanguage['ID']}", file=fout)
					logging.warning(f"\t{sublanguage['ID']} with {len(sublanguage)} values")
					for parameter in sublanguage:
						if not parameter in ["ID", "Glottocode"]:
							# print(f"\t\t{parameter}: {sublanguage[parameter]}", file=fout)
							print(f"\t\t{parameter}", file=fout)
							for sublanguage2 in glotto_wals[language]:
								if parameter not in sublanguage2:
									print(f"\t\t\tMISSING FROM: {sublanguage2['ID']}", file=fout)
								elif sublanguage[parameter] != sublanguage2[parameter]:
									print(f"\t\t\tDIFFERENT VALUE: {sublanguage2['ID']}", file=fout)


	#GRAMBANK
	grambank_languages = u.read_csv(grambank_dirpath.joinpath("languages.csv"), "ID")
	grambank_parameters = u.read_csv(grambank_dirpath.joinpath("parameters.csv"), "ID")
	grambank_codes = u.read_csv(grambank_dirpath.joinpath("codes.csv"), "ID")
	grambank_values = u.read_csv(grambank_dirpath.joinpath("values.csv"), "ID")

	grambank_tosave = {}

	logging.info(f"Reading Grambank data, {len(grambank_languages)} items found")
	logging.info(f"Reading Grambank data, {len(grambank_parameters)} parameters found")
	# input()

	for element_id, element in grambank_values.items():
		language = element["Language_ID"]
		if not language in grambank_tosave:
			grambank_tosave[language] = {}
		parameter = element["Parameter_ID"]
		value = element["Value"]
		if not value == "?":
			# grambank_languages[language][f"G:{grambank_parameters[parameter]['Name']}"] = grambank_codes[f"{parameter}-{value}"]["Description"]
			grambank_tosave[language][f"G:{grambank_parameters[parameter]['Name']}"] = grambank_codes[f"{parameter}-{value}"]["Description"]
		# parameters.add(f"GR-PARAM:{grambank_parameters[parameter]['Name']}")
		if not value == "?":
			parameters["GRAMBANK"][f"{grambank_parameters[parameter]['Name']}"].add(grambank_codes[f"{parameter}-{value}"]["Description"])



	logging.info("Building complete set of languages...")

	complete = {}
	for glottocode in glottocodes:
		found_params = False
		# unique_id = uuid.uuid4()
		if glottocode in glottoisomap:
			complete_lang = {}

			# grambank
			if glottocode in grambank_tosave:
				found_params = True
				complete_lang.update(grambank_tosave[glottocode])
				del grambank_tosave[glottocode]

			# glotto wals 1
			if glottocode in glotto_wals:
				found_params = True
				max_index = 0
				if len(glotto_wals[glottocode]) > 1:
					lens = [len(x) for x in glotto_wals[glottocode]]
					max_index = lens.index(max(lens))
					logging.warning(f"Glottocode {glottocode} has {len(lens)} WALS languages, keeping only the most complete one with id: {glotto_wals[glottocode][max_index]['ID']}")

				lang = glotto_wals[glottocode][max_index]
				complete_lang.update(lang)
				del glotto_wals[glottocode]

				# complete[glottocode]["WALS"] = glotto_wals[glotto]
				# for wals_language in glotto_wals[glotto]:
				# 	del wals_languages[wals_language["ID"]]
				# del glotto_wals[glotto]

			isocode = glottoisomap[glottocode]["ISO639P3code"]
			complete_lang["iso639-3"] = isocode
			# if "iso639-3" in element:
			# 	iso_code = element["iso639-3"]

			# ethnologue
			if isocode in ethnologue:
				complete_lang["written_status"] = ethnologue[isocode]["Written"]
				del ethnologue[isocode]
			else:
				logging.warning(f"ISO code {isocode} not found in ethnologue, {len(complete_lang)} parameters so far")
				# input()

			# 	# noglotto wals
			# 	found_wals = []
			# 	for wals_language_pos, wals_language in enumerate(noglotto_wals):
			# 		if wals_language["ISO639P3code"] == iso_code:
			# 			if not "WALS" in complete[unique_id]:
			# 				complete[unique_id]["WALS"] = []
			# 			complete[unique_id]["WALS"].append(wals_language)
			# 			found_wals.append(wals_language_pos)
			# 	for i in found_wals:
			# 		wals_id = noglotto_wals[i]["ID"]
			# 		del wals_languages[wals_id]
			# 	noglotto_wals = [x for i, x in enumerate(noglotto_wals) if not i in found_wals]

			# 	if glotto in glotto_wals:
			# 		if not "WALS" in complete[unique_id]:
			# 			complete[unique_id]["WALS"] = []
			# 		complete[unique_id]["WALS"].extend(glotto_wals[glotto])
			# 		for wals_language in glotto_wals[glotto]:
			# 			del wals_languages[wals_language["ID"]]
			# 		del glotto_wals[glotto]
			if found_params:
				complete[glottocode] = complete_lang
	logging.info(f"After first mapping, {len(complete)} languages mapped.")
	logging.info(f"There remain: {len(ethnologue)} ethnologue items, {len(glotto_wals)+len(noglotto_wals)} WALS items, {len(grambank_tosave)} Grambank items to be mapped")
	input()

	# logging.info("Finding WALS best match based on ISO_code")

	# glotto wals 1
	glotto_to_delete = []
	for wals_code, wals_langs in glotto_wals.items():
		found = False
		for lang in wals_langs:
			if "ISO639P3code" in lang:
				ID = lang["ID"]
				for compl_id, compl_lang in complete.items():
					if "MAP" in compl_lang and "iso639-3" in compl_lang["MAP"]:
						iso_code = compl_lang["MAP"]["iso639-3"]
						if iso_code == lang["ISO639P3code"]:
							found = True
							if not "WALS" in compl_lang:
								compl_lang["WALS"] = []
							compl_lang["WALS"].append(lang)
		if found:
			glotto_to_delete.append(wals_code)

	for code in glotto_to_delete:
		for wals_language in glotto_wals[code]:
			del wals_languages[wals_language["ID"]]
		del glotto_wals[code]

	to_remove = set()
	for i, wals_lang in enumerate(noglotto_wals):
		iso_codes = wals_lang["ISO_codes"].split()

		found = False
		for element_id, element in complete.items():
			if "iso639-3" in element["MAP"]:
				if any(x==element["MAP"]["iso639-3"] for x in iso_codes):
					if not "WALS" in element:
						element["WALS"] = []
					element["WALS"].append(wals_lang)
					to_remove.add(i)
					found = True
		if found:
			del wals_languages[wals_lang["ID"]]

	noglotto_wals = [x for i, x in enumerate(noglotto_wals) if not i in to_remove]

	# logging.info(f"After second mapping, there remain: {len(ethnologue)} ethnologue items, {len(wals_languages)} WALS items, {len(grambank_languages)} Grambank items to be mapped")


	with open(output_dir.joinpath("notmapped_ethnologue.json"), "w") as fout:
		json.dump(ethnologue, fout, ensure_ascii=False, indent=4)

	with open(output_dir.joinpath("notmapped_wals.json"), "w") as fout:
		json.dump(wals_languages, fout, ensure_ascii=False, indent=4)

	with open(output_dir.joinpath("notmapped_grambank.json"), "w") as fout:
		json.dump(grambank_languages, fout, ensure_ascii=False, indent=4)

	with open(output_dir.joinpath("parameters.tsv"), "w") as fout:
		for source, d in parameters.items():
			for param, values in d.items():
				print(f"{source}\t{param}\t{len(values)}\t{' | '.join(values)}", file=fout)

	discarded = {}
	considered = {}

	for unique_id, language in complete.items():
		if "ETHNOLOGUE" in language and ("WALS" in language or "GRAMBANK" in language):
			considered[language["ETHNOLOGUE"]["ISO 639"]] = language
		else:
			discarded[str(unique_id)] = language

	# logging.info(f"End of computation, {len(considered)} languages mapped, {len(discarded)} languages discarded")

	with open(output_dir.joinpath("language_info.txt"), "w") as fout:
		for language_code in considered:
			wals = 0
			if "WALS" in considered[language_code]:
				wals = len(considered[language_code]["WALS"])
			print(f"{language_code}, {'GRAMBANK' in considered[language_code]}, {'WALS' in considered[language_code]}, {wals}", file=fout)


	with open(output_dir.joinpath("mapped_languages.json"), "w") as fout:
		json.dump(considered, fout, ensure_ascii=False, indent=4)

	with open(output_dir.joinpath("discarded_languages.json"), "w") as fout:
		json.dump(discarded, fout, ensure_ascii=False, indent=4)


if __name__ == "__main__":
	build_db(
		"/home/ludop/Documents/langmapping_project/glottolog-cldf/cldf/languages.csv",
		"/home/ludop/Documents/langmapping_project/data/ethnologue.csv",
		"/home/ludop/Documents/langmapping_project/data/written.csv",
		pathlib.Path("/home/ludop/Documents/langmapping_project/wals/cldf/"),
		pathlib.Path("/home/ludop/Documents/langmapping_project/grambank/cldf/"),
		pathlib.Path("/home/ludop/Documents/langmapping_project/data/")
	)