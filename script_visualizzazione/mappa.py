import lingtypology
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import copy
import random
import collections


# # c'è un bug in stroke features
# stroke_features = ['Ergative', 'Ergative', 'Accusative', 'Accusative', 'Accusative']
# languages = ["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"]
# features = ["Agglutinative", "Agglutinative", "Inflected", "Inflected", "Analytic"]
# m = lingtypology.LingMap(languages)
# m.add_features(features)
# m.add_stroke_features(stroke_features)
# m.create_map()
# m.save('mappe/boh.html')


#colori
#/* CSS HEX */
#--tangelo: #f6511dff;
#--selective-yellow: #ffb400ff;
#--picton-blue: #00a6edff;
#--apple-green: #7fb800ff;
#--berkeley-blue: #0d2c54ff;


# ! CAMBIARE IN "True" SE SI VUOLE FILTRARE I PARAMETRI PER TENERE SOLO QUELLI NEL FILE PARAMETRI_ANNOTATI
# _FILTRO_PARAMETRI = False
_FILTRO_PARAMETRI = True

# STEP1: leggere parametri dal file con annotazioni
reader = csv.DictReader(open('csvs/parametri_annotati_completo.csv', 'r'),
delimiter="\t")
# quotechar='"')
classi = collections.defaultdict(int)
parameters = {}
for line in reader:
	parameters[line["Parametro"]] = line["Classe"]
	classi[line["Classe"]] += 1

print ("TOTALE PARAMETRI ANNOTATI: ", len(parameters))

for classe in classi:
	print(f"### {classe}: {classi[classe]}")

reader = csv.DictReader(open('csvs/mapping.csv', 'r'),
delimiter="\t",
quotechar='"')

# Languages contiene l'intero DB
parametri_nelle_lingue = set()
languages = {}
for line in reader:
	line["coverage"] = float(line["coverage"])
	line["valued_params"] = int(line["valued_params"])

	if _FILTRO_PARAMETRI:
		filtered_line = {"coverage": 0, "valued_params": 0, "Glottocode": line["Glottocode"], "written_status": line["written_status"]}
		for param in line:
			parametri_nelle_lingue.add(param)
			if param.startswith("G:") or param.startswith("W:"):
				if param in parameters:
					filtered_line[param] = line[param]
					if filtered_line[param] != "_":
						filtered_line["valued_params"] += 1

		filtered_line["coverage"] = filtered_line["valued_params"] / len(parameters)

		line = filtered_line

	glottocode = line["Glottocode"]
	if not glottocode in languages:
		languages[glottocode] = line

	# così facendo, in caso di più righe associate a un unico glottocode, prendiamo il coverage maggiore
	if line["coverage"] > languages[glottocode]["coverage"]:
		languages[glottocode] = line

print("Numero di lingue prima del filtro", len(languages))

languages = {x:y for x, y in languages.items() if y["coverage"] > 0}

print("### Lingue totali: ", len(languages))


# DISTRIBUZIONE DI COVERAGE
dist_discrete = [x["valued_params"] for _, x in languages.items()]
dist_continuous = [x["coverage"] for _, x in languages.items()]

plot = sns.ecdfplot(dist_continuous)
plot.set_title("Distribuzione di copertura dei parametri")
plot.figure.savefig("plots parametri/parametri.png", dpi=300)
plt.close(plot.figure)

plot = sns.histplot(dist_discrete)
plot.set_title("Distribuzione di copertura dei parametri - istogramma")
plt.ylim(0, len(languages))
plot.figure.savefig("plots parametri/parametri_istogramma.png", dpi=300)
plt.close(plot.figure)

#prendiamo 33esimo e 66esimo percentile per creare i  bin
q33, q66 = np.percentile(dist_discrete, [33, 66])
q33 = q33
q66 = q66
print(f"### 33esimo percentile: {q33}")
print(f"### 66esimo percentile: {q66}")

average = sum(dist_continuous)/len(dist_continuous)
std = np.std(dist_continuous)
print(f"### Average: {average}")
print(f"### Std: {std}")

for language, language_dict in languages.items():
	valued_params = language_dict["valued_params"]
	coverage = language_dict["coverage"]

	if valued_params <= q33:
		languages[language]["coverage_bin"] = "Low"
	elif valued_params <= q66:
		languages[language]["coverage_bin"] = "Medium"
	else:
		languages[language]["coverage_bin"] = "High"

	# print(language, languages[language]["valued_params"], languages[language]["coverage_bin"])
	# input()
	if coverage <= average - std:
		languages[language]["coverage_bin2"] = "Low"
	elif coverage <= average + std:
		languages[language]["coverage_bin2"] = "Medium"
	else:
		languages[language]["coverage_bin2"] = "High"


print("### (Percentili) Lingue con value: HIGH - ", len([x for x in languages.values() if x["coverage_bin"] == "High"]))
print("### (Percentili) Lingue con value: MEDIUM - ", len([x for x in languages.values() if x["coverage_bin"] == "Medium"]))
print("### (Percentili) Lingue con value: LOW - ", len([x for x in languages.values() if x["coverage_bin"] == "Low"]))

print("### (Media+/-std) Lingue con value: HIGH - ", len([x for x in languages.values() if x["coverage_bin2"] == "High"]))
print("### (Media+/-std) Lingue con value: MEDIUM - ", len([x for x in languages.values() if x["coverage_bin2"] == "Medium"]))
print("### (Media+/-std) Lingue con value: LOW - ", len([x for x in languages.values() if x["coverage_bin2"] == "Low"]))


# # ! MAPPA 1: tutti i pallini senza i bin
# m = lingtypology.LingMap(languages.keys(), glottocode=True)
# m.title = 'Mappa 1'
# m.add_features([x["coverage"] for _, x in languages.items()],
# 				numeric=True,
# 				colors=lingtypology.gradient(10, 'white', 'green'))
# m.legend_position = 'topright'
# m.legent_title = "Legend"
# m.create_map()
# m.save('mappe/mappa-1.html')

# print("#### PRODOTTO MAPPA 1 ####")

# # ! MAPPA 2a: tutti i pallini con i bin - percentile
# m = lingtypology.LingMap(languages.keys(), glottocode=True)
# m.title = 'Mappa 2a'
# m.add_features([x["coverage_bin"] for _, x in languages.items()],
# 				colors=("#FF0000", "#FFFF00", "#00FF00"),
# 				factor=('Low', 'Medium', 'High'),
# 				control=True)
# m.legend_position = 'topright'
# m.legent_title = "Legend"
# m.create_map()
# m.save('mappe/mappa-2a.html')

# print("#### PRODOTTO MAPPA 2a ####")

# # ! MAPPA 2b: tutti i pallini con i bin - media +/- std
# m = lingtypology.LingMap(languages.keys(), glottocode=True)
# m.title = 'Mappa 2b'
# m.add_features([x["coverage_bin2"] for _, x in languages.items()],
# 				colors=("#FF0000", "#FFFF00", "#00FF00"),
# 				factor=('Low', 'Medium', 'High'),
# 				control=True)
# m.legend_position = 'topright'
# m.legent_title = "Legend"
# m.create_map()
# m.save('mappe/mappa-2b.html')

# print("#### PRODOTTO MAPPA 2b ####")

# for written_status in ["Written", "Primarily oral", "don't know"]:

# 	# ! MAPPA 2a: tutti i pallini con i bin - percentile
# 	m = lingtypology.LingMap([glotto for glotto, x in languages.items() if x["written_status"] == written_status], glottocode=True)
# 	m.title = f"Mappa 2a - {written_status}"
# 	m.add_features([x["coverage_bin"] for _, x in languages.items() if x["written_status"] == written_status],
# 					colors=("#FF0000", "#FFFF00", "#00FF00"),
# 					factor=('Low', 'Medium', 'High'),
# 					control=True)
# 	m.legend_position = 'topright'
# 	m.legent_title = "Legend"
# 	m.create_map()
# 	m.save(f"mappe/mappa-2a-{written_status}.html")

# 	print(f"#### PRODOTTO MAPPA 2a-{written_status} ####")

# 	# ! MAPPA 2b: tutti i pallini con i bin - media +/- std
# 	m = lingtypology.LingMap([glotto for glotto, x in languages.items() if x["written_status"] == written_status], glottocode=True)
# 	m.title = f"Mappa 2b - {written_status}"
# 	m.add_features([x["coverage_bin2"] for _, x in languages.items() if x["written_status"] == written_status],
# 					colors=("#FF0000", "#FFFF00", "#00FF00"),
# 					factor=('Low', 'Medium', 'High'),
# 					control=True)
# 	m.legend_position = 'topright'
# 	m.legent_title = "Legend"
# 	m.create_map()
# 	m.save(f"mappe/mappa-2b-{written_status}.html")

# 	print(f"#### PRODOTTO MAPPA 2b-{written_status} ####")



for classe in classi:

	print("@@@", classe, "@@@", " parametri:", classi[classe])

	filtered_languages = {}
	for language, language_dict in languages.items():
		filtered_languages[language] = {}
		n_params = 0
		for param in language_dict:
			if param in parameters \
				and parameters[param] == classe \
					and language_dict[param] != "_":
				n_params += 1
				filtered_languages[language][param] = language_dict[param]

		filtered_languages[language]["valued_params"] = n_params
		filtered_languages[language]["coverage"] = n_params/classi[classe]
		filtered_languages[language]["written_status"] = language_dict["written_status"]

	to_remove = set()
	for language in filtered_languages:
		if filtered_languages[language]["valued_params"] == 0:
			to_remove.add(language)

	# DISTRIBUZIONE DI COVERAGE
	dist_discrete = [x["valued_params"] for _, x in filtered_languages.items()]
	dist_continuous = [x["coverage"] for _, x in filtered_languages.items()]
	plot = sns.ecdfplot(dist_continuous)
	plot.set_title("Distribuzione di copertura dei parametri")
	plt.ylim(0, len(languages))
	plot.figure.savefig(f"plots parametri/parametri_{classe}.png.png", dpi=300)
	plt.close(plot.figure)

	plot = sns.histplot(dist_discrete)
	plot.set_title("Distribuzione di copertura dei parametri - istogramma")
	plot.figure.savefig(f"plots parametri/parametri_istogramma_{classe}.png", dpi=300)
	plt.close(plot.figure)

	#prendiamo 33esimo e 66esimo percentile per creare i  bin
	q33, q66 = np.percentile(dist_discrete, [33, 66])
	q33 = q33
	q66 = q66
	print(f"### 33esimo percentile: {q33}")
	print(f"### 66esimo percentile: {q66}")

	average = sum(dist_continuous)/len(dist_continuous)
	std = np.std(dist_continuous)
	print(f"### Average: {average}")
	print(f"### Std: {std}")

	for language, language_dict in filtered_languages.items():
		valued_params = language_dict["valued_params"]
		coverage = language_dict["coverage"]

		if valued_params <= q33:
			filtered_languages[language]["coverage_bin"] = "Low"
		elif valued_params <= q66:
			filtered_languages[language]["coverage_bin"] = "Medium"
		else:
			filtered_languages[language]["coverage_bin"] = "High"

		if coverage <= average - std:
			filtered_languages[language]["coverage_bin2"] = "Low"
		elif coverage <= average + std:
			filtered_languages[language]["coverage_bin2"] = "Medium"
		else:
			filtered_languages[language]["coverage_bin2"] = "High"

	for glottocode in to_remove:
		del filtered_languages[glottocode]

	print(f"Lingue con almeno un parametro di classe {classe}: ", len(filtered_languages))

	features = [x["coverage_bin"] for _, x in filtered_languages.items()]

# 	# ! MAPPA 3: tutti i pallini senza i bin
# 	m = lingtypology.LingMap(filtered_languages.keys(), glottocode=True)
# 	m.title = 'Mappa 1'
# 	m.add_features([x["coverage"] for _, x in filtered_languages.items()],
# 					numeric=True,
# 					colors=lingtypology.gradient(10, 'white', 'green'))
# 	m.legend_position = 'topright'
# 	m.legent_title = "Legend"
# 	m.create_map()
# 	m.save(f'mappe/mappa-3-{classe}.html')

# 	for written_status in ["Written", "Primarily oral", "don't know"]:
# 		# ! MAPPA 3a: tutti i pallini senza i bin
# 		m = lingtypology.LingMap([glotto for glotto, x in filtered_languages.items() if x["written_status"] == written_status], glottocode=True)
# 		m.title = 'Mappa 1'
# 		m.add_features([x["coverage"] for _, x in filtered_languages.items() if x["written_status"] == written_status],
# 						numeric=True,
# 						colors=lingtypology.gradient(10, 'white', 'green'))
# 		m.legend_position = 'topright'
# 		m.legent_title = "Legend"
# 		m.create_map()
# 		m.save(f'mappe/mappa-3-{classe}-{written_status}.html')



# # ! MAPPA 4: tutti i pallini scritto/parlato
# m = lingtypology.LingMap(languages.keys(), glottocode=True)
# m.title = 'Mappa 3'
# m.add_features([x["written_status"] for _, x in languages.items()],
# 			control=True,
# 			colors=("#7C0B2B", "#FFCBDD", "#FB4B4E"))
# m.create_map()
# m.save('mappe/mappa-4.html')
