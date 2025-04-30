import lingtypology
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import copy
import random
import collections


#colori
#/* CSS HEX */
#--tangelo: #f6511dff;
#--selective-yellow: #ffb400ff;
#--picton-blue: #00a6edff;
#--apple-green: #7fb800ff;
#--berkeley-blue: #0d2c54ff;

reader = csv.DictReader(open('csvs/mapping.csv', 'r'), delimiter="\t")
n_parameters = 0

# Languages contiene l'intero DB
languages = {}
for line in reader:
	line["coverage"] = float(line["coverage"])
	line["valued_params"] = int(line["valued_params"])
	coverage = float(line["coverage"])

	if not line["Glottocode"] in languages:
		languages[line["Glottocode"]] = line

	# così facendo, in caso di più righe associate a un unico glottocode, prendiamo il coverage maggiore
	if coverage > languages[line["Glottocode"]]["coverage"]:
		languages[line["Glottocode"]] = line

for el in line:
	if el.startswith("G:") or el.startswith("W:"):
		n_parameters += 1

print("### Lingue totali: ", len(languages))

# MAPPA 1: tutti i pallini senza i bin

m = lingtypology.LingMap(languages.keys(), glottocode=True)
m.title = 'Mappa 1'
m.add_features([x["coverage"] for _, x in languages.items()], numeric=True, colors=lingtypology.gradient(100, 'white', 'green'))
m.create_map()
m.save('mappe/mappa-1.html')


# DISTRIBUZIONE DI COVERAGE

dist1 = [x["valued_params"] for _, x in languages.items()]
dist = [x["coverage"] for _, x in languages.items()]
# plot = sns.displot(dist)
plot = sns.ecdfplot(dist)
# plt.ylim(0, len(languages))
plot.figure.savefig("plots parametri/parametri.png", dpi=300)
plt.close(plot.figure)


#prendiamo 33esimo e 66esimo percentile per creare i  bin
q33, q66 = np.percentile(dist1, [33, 66])
q33 = q33
q66 = q66
print(f"### 33esimo percentile: {q33}")
print(f"### 66esimo percentile: {q66}")


# MAPPA 2: tutti i pallini con i bin

languages_binned = {}
for language, language_dict in languages.items():
	languages_binned[language] = copy.deepcopy(language_dict)
	valued_params = language_dict["valued_params"]

	if valued_params <= q33:
		languages_binned[language]["coverage"] = "Low"
	elif valued_params <= q66:
		languages_binned[language]["coverage"] = "Medium"
	else:
		languages_binned[language]["coverage"] = "High"


print("### Lingue con value: HIGH - ", len([x for x in languages_binned.values() if x["coverage"] == "High"]))
print("### Lingue con value: MEDIUM - ", len([x for x in languages_binned.values() if x["coverage"] == "Mdium"]))
print("### Lingue con value: LOW - ", len([x for x in languages_binned.values() if x["coverage"] == "Low"]))

# m = lingtypology.LingMap(languages_binned.keys(), glottocode=True)
# m.title = 'Mappa 2'
# m.add_features([x["coverage"] for _, x in languages_binned.items()],
# 				colors=("#FF0000", "#FFFF00", "#00FF00"),
# 				factor=('Low', 'Medium', 'High'),
# 				control=True)
# m.create_map()
# m.save('mappe/mappa-2.html')


reader = csv.DictReader(open('csvs/parametri_annotati.csv', 'r'), delimiter="\t", quotechar='"')
classi = collections.defaultdict(int)
parameters = {}
for line in reader:
	parameters[line["Parametro"]] = line["Classe"]
	classi[line["Classe"]] += 1

for classe in classi:
	print(f"### {classe}: {classi[classe]}")

for classe in classi:

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

	dist = [x["coverage"] for _, x in filtered_languages.items()]
	plot = sns.ecdfplot(dist)
	plot.figure.savefig(f"plots parametri/parametri_{classe}.png", dpi=300)
	plt.close(plot.figure)






# MAPPA 3: tutti i pallini scritto/parlato

m = lingtypology.LingMap(languages.keys(), glottocode=True)
m.title = 'Mappa 3'
m.add_features([x["written_status"] for _, x in languages.items()],
			control=True,
			colors=("#7C0B2B", "#FFCBDD", "#FB4B4E"))
m.create_map()
m.save('mappe/mappa-3.html')




# MAPPA 4: stroke features

# m = lingtypology.LingMap(languages_binned.keys(), glottocode=True)
# m.title = 'Mappa 4'
# m.add_features([x["coverage"] for _, x in languages_binned.items()],
# 				colors=("#FF0000", "#FFFF00", "#00FF00"),
# 				factor=('Low', 'Medium', 'High'),
# 				control=True)
# m.add_stroke_features([x["written_status"] for _, x in languages_binned.items()])
# m.create_map()
# m.save('mappe/mappa-4.html')








# language_coverage_bin = {}

# for glottocode, coverage in language_coverage.items():
# 	if coverage <= 0.3:
# 		language_coverage_bin[glottocode] = 1
# 	elif coverage <= 0.6:
# 		language_coverage_bin[glottocode] = 2
# 	else:
# 		language_coverage_bin[glottocode] = 3

# m = lingtypology.LingMap(language_coverage_bin.keys(), glottocode=True)
# m.add_features(language_coverage_bin.values(), numeric=True, colors=lingtypology.gradient(100, 'white', 'red'))
# # m.add_features(native_speakers, numeric=True, colors=lingtypology.gradient(100, 'white', 'red'))

# #m.save_static(fname="mappa.png")

# # COLOR GRADIENT
# # m.add_features(native_speakers, numeric=True)
# # m.colormap_colors = ('white', 'red')