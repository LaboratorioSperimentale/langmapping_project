import lingtypology
import csv
import random

reader = csv.DictReader(open('dati.csv', 'r'))
languages = []
features = []
native_speakers = []

for line in reader:
	languages.append(line['Language'])
	features.append(line['Word order'])
	native_speakers.append(int(random.randint(100, 100000)))

print(native_speakers)

m = lingtypology.LingMap(languages)
m.add_features(features, control=True)
m.add_features(native_speakers, numeric=True, colors=lingtypology.gradient(100, 'white', 'red'))
m.create_map()
m.save('map.html')
#m.save_static(fname="mappa.png")

# COLOR GRADIENT
# m.add_features(native_speakers, numeric=True)
# m.colormap_colors = ('white', 'red')