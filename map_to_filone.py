import json
import csv

data = json.loads(open("output/merged_languages/mapped_languages.json").read())


full_header = []
with open("output/csv_header.sorted.txt") as fin:
	lines = fin.readlines()

	for line in lines:
		full_header.append(line.strip())
# 	print(lines[:10])
# 	input()

# full_header = set()
# full_header.add("ID")

plain_data = []

for lang_id in data:
	# print(lang_id)

	curr_data = {"ID": lang_id}
	# plain_data[lang_id] = {}

	for subpar in data[lang_id]:

		if subpar == "WALS":
			for el in data[lang_id][subpar]:
				for subpar_k in el:
					curr_data[f"{subpar}-{subpar_k}"] = el[subpar_k]
					# full_header.add(f"{subpar}-{subpar_k}")
		else:

			for subpar_k in data[lang_id][subpar]:
				curr_data[f"{subpar}-{subpar_k}"] = data[lang_id][subpar][subpar_k]
				# full_header.add(f"{subpar}-{subpar_k}")

	plain_data.append(curr_data)
	# print(lang_id)
	# print(plain_data)
	# input()



with open('output/TABELLONA.csv', 'w', encoding="utf-8") as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=full_header)
	writer.writeheader()

	for item in plain_data:
		writer.writerow(item)