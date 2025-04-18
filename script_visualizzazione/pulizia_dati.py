import csv
import json

print("Glottocode,Written")

with open("../data/mapped_languages.json") as fin:
	languages_data = json.loads(fin.read())

	for datum, parameters in languages_data.items():
		glottocode = None
		if "WALS" in parameters:
			wals = parameters["WALS"]
			for sublanguage in wals:
				if len(sublanguage["Glottocode"]):
					glottocode = sublanguage["Glottocode"]

		if glottocode:
			print(f"{glottocode},{parameters['ETHNOLOGUE']['Written']}")
		# input()