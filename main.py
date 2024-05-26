import argparse
import pathlib

import json
import pandas as pd

import lmp.ethnologue as eth
import lmp.build as build


# def _guess_written(args):
# 	input_file = args.ethnologue_dump
# 	data = json.loads(open(input_file, encoding="utf-8").read())

# 	eth.guess_written(data, args.output_dir)


def _written_parameters(args):
	input_file = args.ethnologue_dump
	data = json.loads(open(input_file, encoding="utf-8").read())

	eth.written_parameters(data, args.output_dir)

def _convert_to_csv(args):
	input_file = args.input_file

	df = pd.read_json(open(input_file, encoding="utf-8")).T
	df.to_csv(args.output_file, encoding='utf-8', index=False)


def _build_db(args):

	build.build_db(args.iso_glotto_map, args.ethnologue,
				args.written_status,
				args.wals_dir, args.grambank_dir,
				args.output_dir)



if __name__ == "__main__":
	parent_parser = argparse.ArgumentParser(add_help=False)

	root_parser = argparse.ArgumentParser(prog='lmp', add_help=True)
	subparsers = root_parser.add_subparsers(title="actions", dest="actions")


	parser_guesswriting = subparsers.add_parser('guess-written', parents=[parent_parser],
											 	description='run NLP Pipeline',
											 	help='run NLP Pipeline')
	parser_guesswriting.add_argument("-e", "--ethnologue_dump", required=True,
								  type=pathlib.Path,
								  help="path to ethnologue dump in json format")
	parser_guesswriting.add_argument("-o", "--output-dir", default="output/",
								  type=pathlib.Path,
								  help="path to folder to store output")
	# parser_guesswriting.set_defaults(func=_guess_written)
	parser_guesswriting.set_defaults(func=_written_parameters)


	parser_convert = subparsers.add_parser('convert', parents=[parent_parser],
											description='convert to csv',
											help='convert to csv')
	parser_convert.add_argument("-i", "--input-file", type=pathlib.Path, required=True)
	parser_convert.add_argument("-o", "--output-file", type=pathlib.Path, required=True)
	parser_convert.set_defaults(func=_convert_to_csv)

	parser_buildmap = subparsers.add_parser("build-map", parents=[parent_parser],
										 description="build complete map from sources",
										 help="builds complete map from sources")
	parser_buildmap.add_argument("-o", "--output-dir", type=pathlib.Path, default="output/")
	parser_buildmap.add_argument("--iso-glotto-map", type=pathlib.Path, required=True,
							  default="data/iso-glotto-map.json",
							  help="json file containing map of isocodes to glottocodes")
	parser_buildmap.add_argument("--ethnologue", type=pathlib.Path, required=True,
							  help="Ethnologue data in csv format")
	parser_buildmap.add_argument("--written-status", type=pathlib.Path, required=True,
							  help="csv file containing infomration about written status of ethnologue languages")
	parser_buildmap.add_argument("--wals-dir", type=pathlib.Path, required=True,
							  help="path to folder containing wals data")
	parser_buildmap.add_argument("--grambank-dir", type=pathlib.Path, required=True,
							  help="path to folder containing grambank data")
	parser_buildmap.set_defaults(func=_build_db)

	args = root_parser.parse_args()
	if "func" not in args:
		root_parser.print_usage()
		exit()
	args.func(args)