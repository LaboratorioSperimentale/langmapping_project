import json
import collections
import uuid

import lmp.utils as u


def build_db(iso_glotto_fname, ethnologue_fname,
			 written_status_fname,
			 wals_dirpath, grambank_dirpath,
			 output_dir):

	parameters = {"WALS": collections.defaultdict(lambda: set()),
			   	  "GRAMBANK": collections.defaultdict(lambda: set())}

	#MAP
	isoglottomap = u.read_json(iso_glotto_fname)

	# logging.info(f"Reading iso-glotto map, {len(isoglottomap)} items found")

	#ETHNOLOGUE
	ethnologue = u.read_csv(ethnologue_fname, key="ISO 639")
	written_data = u.read_csv(written_status_fname, key="ISO 639")
	for lang_id, lang in ethnologue.items():
		lang["Written"] = written_data[lang_id]["status"]


	#WALS
	wals_languages = u.read_csv(wals_dirpath.joinpath("languages.csv"), "ID")
	wals_parameters = u.read_csv(wals_dirpath.joinpath("parameters.csv"), "ID")
	wals_codes = u.read_csv(wals_dirpath.joinpath("codes.csv"), "ID")
	wals_values = u.read_csv(wals_dirpath.joinpath("values.csv"), "ID")

	# logging.info(f"Reading WALS data, {len(wals_languages)} items found")
	# logging.info(f"Reading WALS data, {len(wals_parameters)} parameters found")

	for element_id, element in wals_values.items():
		language = element["Language_ID"]
		parameter = element["Parameter_ID"]
		value = element["Value"]
		wals_languages[language][f"PARAM:{wals_parameters[parameter]['Name']}"] = wals_codes[f"{parameter}-{value}"]["Description"]

		parameters["WALS"][f"{wals_parameters[parameter]['Name']}"].add(wals_codes[f"{parameter}-{value}"]["Description"])

	glotto_wals = {}
	noglotto_wals = []
	for language_id, language in wals_languages.items():
		if len(language["Glottocode"]) > 0:
			if not language["Glottocode"] in glotto_wals:
				glotto_wals[language["Glottocode"]] = []
			glotto_wals[language["Glottocode"]].append(language)
		else:
			noglotto_wals.append(language)

	# logging.info(f"Among WALS languages, {len(wals_languages)-len(noglotto_wals)} have glottocode and {len(noglotto_wals)} do not")
	# logging.info(f"Total number of ISO codes found in WALS: {len(glotto_wals)}")

	#GRAMBANK
	grambank_languages = u.read_csv(grambank_dirpath.joinpath("languages.csv"), "ID")
	grambank_parameters = u.read_csv(grambank_dirpath.joinpath("parameters.csv"), "ID")
	grambank_codes = u.read_csv(grambank_dirpath.joinpath("codes.csv"), "ID")
	grambank_values = u.read_csv(grambank_dirpath.joinpath("values.csv"), "ID")

	# logging.info(f"Reading Grambank data, {len(grambank_languages)} items found")
	# logging.info(f"Reading Grambank data, {len(grambank_parameters)} parameters found")

	for element_id, element in grambank_values.items():
		language = element["Language_ID"]
		parameter = element["Parameter_ID"]
		value = element["Value"]
		if not value == "?":
			grambank_languages[language][f"PARAM:{grambank_parameters[parameter]['Name']}"] = grambank_codes[f"{parameter}-{value}"]["Description"]
		# parameters.add(f"GR-PARAM:{grambank_parameters[parameter]['Name']}")
		if not value == "?":
			parameters["GRAMBANK"][f"{grambank_parameters[parameter]['Name']}"].add(grambank_codes[f"{parameter}-{value}"]["Description"])



	# logging.info("Building complete set of languages")

	complete = {}
	for element_id, element in isoglottomap.items():
		unique_id = uuid.uuid4()
		complete[unique_id] = {"MAP": element}

		glotto = element_id

		# grambank
		if glotto in grambank_languages:
			complete[unique_id]["GRAMBANK"] = grambank_languages[glotto]
			del grambank_languages[glotto]

		# glotto wals 1
		if glotto in glotto_wals:
			complete[unique_id]["WALS"] = glotto_wals[glotto]
			for wals_language in glotto_wals[glotto]:
				del wals_languages[wals_language["ID"]]
			del glotto_wals[glotto]


		if "iso639-3" in element:
			iso_code = element["iso639-3"]

			# ethnologue
			if iso_code in ethnologue:
				complete[unique_id]["ETHNOLOGUE"] = ethnologue[iso_code]
				del ethnologue[iso_code]

			# noglotto wals
			found_wals = []
			for wals_language_pos, wals_language in enumerate(noglotto_wals):
				if wals_language["ISO639P3code"] == iso_code:
					if not "WALS" in complete[unique_id]:
						complete[unique_id]["WALS"] = []
					complete[unique_id]["WALS"].append(wals_language)
					found_wals.append(wals_language_pos)
			for i in found_wals:
				wals_id = noglotto_wals[i]["ID"]
				del wals_languages[wals_id]
			noglotto_wals = [x for i, x in enumerate(noglotto_wals) if not i in found_wals]

			if glotto in glotto_wals:
				if not "WALS" in complete[unique_id]:
					complete[unique_id]["WALS"] = []
				complete[unique_id]["WALS"].extend(glotto_wals[glotto])
				for wals_language in glotto_wals[glotto]:
					del wals_languages[wals_language["ID"]]
				del glotto_wals[glotto]

	# logging.info(f"After first mapping, there remain: {len(ethnologue)} ethnologue items, {len(wals_languages)} WALS items, {len(grambank_languages)} Grambank items to be mapped")

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