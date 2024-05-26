import json
import re

def written_parameters(data, output_dir):
	written_label = {}

	for language, language_data in data.items():
		name = language_data["name"]
		written_label[language] = {}

		writing_system, language_development, language_use = "", "", ""

		if "Writing" in language_data:
			writing_system = language_data["Writing"]
			written_label[language]["WRITING"] = "NOT_EMPTY"
		else:
			written_label[language]["WRITING"] = "EMPTY"

		if "Language Development" in language_data:
			language_development = language_data["Language Development"]
			written_label[language]["DEVELOPMENT"] = "NOT_EMPTY"
		else:
			written_label[language]["DEVELOPMENT"] = "EMPTY"

		if "Language Use" in language_data:
			language_use = language_data["Language Use"]
			written_label[language]["USE"] = "NOT_EMPTY"
		else:
			written_label[language]["USE"] = "EMPTY"

		written_label[language]["SIGN_LANGUAGE"] = 1 if "Sign" in name else 0
		written_label[language]["UNWRITTEN"] = 1 if "Unwritten" in writing_system else 0
		written_label[language]["LITERATURE"] = 1 if "Literature" in language_development else 0
		written_label[language]["NEWSPAPERS"] = 1 if "Newspapers" in language_development else 0
		written_label[language]["TV"] = 1 if "TV" in language_development else 0
		written_label[language]["RADIO"] = 1 if "Radio" in language_development else 0
		written_label[language]["TAUGHT"] = 1 if "Taught in" in language_development else 0
		written_label[language]["SHIFTING"] = 1 if "Shifting" in language_use else 0
		written_label[language]["SHIFTED"] = 1 if "Shifted" in language_use else 0
		written_label[language]["NT"] = 1 if "NT" in language_development else 0
		written_label[language]["OT"] = 1 if "OT" in language_development else 0
		written_label[language]["Bible"] = 1 if "Bible" in language_development else 0
		written_label[language]["Dictionary"] = 1 if "Dictionary" in language_development else 0
		written_label[language]["Grammar"] = 1 if "Grammar" in language_development else 0
		written_label[language]["LITERACY_L1"] = "N/A"
		written_label[language]["LITERACY_L2"] = "N/A"

		m = re.search(r'(?<=Literacy rate in L1: )[^\.]+(\.)', language_development)
		# print(language_development)
		if m:
			written_label[language]["LITERACY_L1"] = str(m.group(0))

		m = re.search(r'(?<=Literacy rate in L2: )[^\.]+(\.)', language_development)
		# print(language_development)
		if m:
			written_label[language]["LITERACY_L2"] = str(m.group(0))

		written_label[language].update({
			"ISO 639": language_data["ISO 639"],
			"name": name,
			"status": guess_written_lang(language, language_data),
			"Writing": writing_system,
			"Language Development": language_development,
			"Language Use": language_use
			})

	sorted_items = sorted(written_label.items(), key=lambda x: x[1]["status"])
	with open(output_dir.joinpath("written_data_parameters.json"), 'w', encoding="utf-8") as outfile:
		json.dump(dict(sorted_items), outfile, indent=4)


def guess_written_lang(language, language_data):

	written = "don't know"
	assigned = 0

	name = language_data["name"]
	writing_system, language_development, language_use = "", "", ""

	if "Writing" in language_data:
		writing_system = language_data["Writing"]

	if "Language Development" in language_data:
		language_development = language_data["Language Development"]

	if "Language Use" in language_data:
		language_use = language_data["Language Use"]

	if "Sign" in name:
		written = "Primarily oral"
		assigned+=1

	elif "Unwritten" in writing_system:
		written = "Primarily oral"
		assigned+=1

	elif "Literature" in language_development or \
		"Newspapers" in language_development or \
		"TV" in language_development or \
		"Radio" in language_development:
		written = "Written"
		assigned+=1

	elif "Taught in" in language_development:
		written = "Written"
		assigned+=1

	elif "Shifting" in language_use or "Shifted" in language_use:
		written = "Primarily oral"
		assigned+=1

	elif ("NT:" in language_development or \
		"OT:" in language_development or \
		"Bible" in language_development or \
		"Dictionary" in language_development or \
		"Grammar" in language_development) and \
		("Literature" not in language_development or \
		"Newspapers" not in language_development or \
		"Radio" not in language_development or \
		"TV" not in language_development):
		written = "Primarily oral"
		assigned+=1

	return written

def guess_written(data, output_dir):
	written_label = {}

	for language, language_data in data.items():

		written = "don't know"
		assigned = 0

		name = language_data["name"]
		writing_system, language_development, language_use = "", "", ""

		if "Writing" in language_data:
			writing_system = language_data["Writing"]

		if "Language Development" in language_data:
			language_development = language_data["Language Development"]

		if "Language Use" in language_data:
			language_use = language_data["Language Use"]

		if "Sign" in name:
			written = "Primarily oral"
			assigned+=1

		elif "Unwritten" in writing_system:
			written = "Primarily oral"
			assigned+=1

		elif "Literature" in language_development or \
			"Newspapers" in language_development or \
			"TV" in language_development or \
			"Radio" in language_development:
			written = "Written"
			assigned+=1

		elif "Taught in" in language_development:
			written = "Written"
			assigned+=1

		elif "Shifting" in language_use or "Shifted" in language_use:
			written = "Primarily oral"
			assigned+=1

		elif ("NT:" in language_development or \
			"OT:" in language_development or \
			"Bible" in language_development or \
			"Dictionary" in language_development or \
			"Grammar" in language_development) and \
			("Literature" not in language_development or \
			"Newspapers" not in language_development or \
			"Radio" not in language_development or \
			"TV" not in language_development):
			written = "Primarily oral"
			assigned+=1

		written_label[language] = {
			"ISO 639": language_data["ISO 639"],
			"name": name,
			"status": written,
			"Writing": writing_system,
			"Language Development": language_development,
			"Language Use": language_use
			}


	sorted_items = sorted(written_label.items(), key=lambda x: x[1]["status"])
	with open(output_dir.joinpath("written_data.json"), 'w', encoding="utf-8") as outfile:
		json.dump(dict(sorted_items), outfile, indent=4)