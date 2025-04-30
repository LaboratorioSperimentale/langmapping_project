import lingtypology
import csv
import random
import math

reader = csv.DictReader(open('csvs/mapping.csv', 'r'), delimiter="\t")

language_coverage = {}

for line in reader:
	if not line["Glottocode"] in language_coverage:
		language_coverage[line["Glottocode"]] = 0
	
	if float(line["coverage"]) > float(language_coverage[line["Glottocode"]]):
		language_coverage[line["Glottocode"]] = float(line["coverage"])
#così facendo, in caso di più righe associate a un unico glottocode, prendiamo il coverage maggiore

language_coverage_bin = {}

for glottocode, coverage in language_coverage.items():
	if coverage <= 0.3:
		language_coverage_bin[glottocode] = "Small"
	elif coverage <= 0.6:
		language_coverage_bin[glottocode] = "Medium"
	else:
		language_coverage_bin[glottocode] = "Large"

for el in ["Small", "Medium", "Large"]:
	latlong = [lingtypology.glottolog.get_coordinates_by_glot_id(x) for x, y in language_coverage_bin.items() if y == el]

	latlong_pulito = []

	for x in latlong:
		if x is not None:
			if not math.isnan(x[0]) and not math.isnan(x[1]):
				latlong_pulito.append(x)
		else:
			print("Removing code")


	m = lingtypology.LingMap()
	m.add_heatmap(latlong_pulito)

	m.save(f'mappa_{el}.html')
#m.save_static(fname="mappa.png")

# COLOR GRADIENT
# m.add_features(native_speakers, numeric=True)
# m.colormap_colors = ('white', 'red')