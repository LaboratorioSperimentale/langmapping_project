import json
import csv

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