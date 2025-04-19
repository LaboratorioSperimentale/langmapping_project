import collections
import json
import csv

def read_glottocodes(filename):
	languages = {}

	with open(filename, encoding="utf-8") as csvfile:
		fin = csv.reader(csvfile, delimiter="\t", quotechar='"')
		header = fin.__next__()

		for line in fin:
			line = dict(zip(header, line))
			d = {}
			if "iso639P3code" in line and line["iso639P3code"]:
				d["iso639-3"] = line["iso639P3code"]

			languages[line["id"]] = d

	return languages


def read_csv(filename, key):

	ret = {}

	with open(filename, encoding="utf-8") as csvfile:
		fin = csv.reader(csvfile, delimiter=',', quotechar='"')
		header = fin.__next__()

		for line in fin:
			line = dict(zip(header, line))

			# for key, value in line.items():
			# 	line[key] = value.replace("\\n", "")

			ret[line[key]] = line

	return ret


def read_json(filename):
	ret = {}

	data = json.load(open(filename, encoding="utf-8"))["resources"]

	for obj in data:
		ret[obj["id"]] = {"id": obj["id"],
						  "name": obj["name"],
						  "latitude": obj["latitude"],
						  "longitude": obj["longitude"],}

		identifiers = obj["identifiers"]
		for ide in identifiers:
			ret[obj["id"]][ide["type"]] = ide["identifier"]

	return ret

def print_analysis_glottowals(glotto_wals, ethnologue, output_dir):
	with open(output_dir.joinpath("glotto_wals.csv"), "w") as fout_csv, open(output_dir.joinpath("glotto_wals.txt"), "w") as fout:

		for language_id, languages in glotto_wals.items():
			if len(languages) > 1:
				shared = collections.defaultdict(lambda: collections.defaultdict(int))
				different_values = collections.defaultdict(lambda: collections.defaultdict(int))
				writer = csv.DictWriter(fout_csv,
										fieldnames = ["ID"]+[subl["ID"] for subl in languages],
										delimiter="\t",
										restval="0")


				tmp = [(subl["ID"], len(subl)-2) for subl in languages]
				isos = []
				for subl in languages:
					if "ISO639P3code" in subl:
						isos.append(subl["ISO639P3code"])
					else:
						isos.append("")
				tmp = [f"{x[0]} ({x[1]} params, {1 if len(y)>0 and y in ethnologue else 0}-eth)" for x,y in zip(tmp, isos)]

				print(f"GLOTTOCODE {language_id} has codes {', '.join(tmp)}", file=fout)
				print(f"GLOTTOCODE {language_id} has isocodes {', '.join(isos)}", file=fout_csv)
				# logging.warning(f"Glottocode {language} has more than one WALS language:")

				for language in languages:

					status = "missing"
					if "ISO639P3code" in language and language['ISO639P3code'] in ethnologue:
						status = ethnologue[language['ISO639P3code']]["Written"]

					print(f"\t{language['ID']} - written status: {status}", file=fout)
					# logging.warning(f"\t{language['ID']} with {len(language)} values")

					for parameter in language:

						if not parameter in ["ISO639P3code", "Glottocode"]:

							missing = []
							different = []

							for language2 in languages:
								if not parameter in language2:
									missing.append(language2["ID"])
								elif language[parameter] != language2[parameter]:
									different.append((language2["ID"], language2[parameter]))
									different_values[language["ID"]][language2["ID"]] += 1
								else:
									shared[language["ID"]][language2["ID"]] += 1

							# if len(missing) > 0 or len(different) > 0:
							if len(different) > 0:
								print(f"\t\t{parameter} - [VALUE: {language[parameter]}]", file=fout)
								# if len(missing) > 0:
									# print(f"\t\t\tMISSING FROM: {' '.join(missing)}", file=fout)
								# elif len(different) > 0:
								strs = [f"{x[0]}: [{x[1]}]" for x in different]
								print(f"\t\t\tDIFFERENT VALUES: {' '.join(strs)}", file=fout)

				print("shared parameters", file=fout_csv)
				writer.writeheader()
				for element in shared:
					writer.writerow({"ID": element, **shared[element]})
				print("different values parameters", file=fout_csv)
				writer.writeheader()
				for element in shared:
					writer.writerow({"ID": element, **different_values[element]})

				print("\n", file=fout)
				print("\n", file=fout_csv)


if __name__ == "__main__":
	read_glottocodes("/home/ludop/Documents/langmapping_project/data/glottocodes.csv")