#!/usr/bin/python

import argparse
import logging
import xml.etree.ElementTree as etree
import json


ID_SUFFIX=".id"
EN_SUFFIX=".en.tok"
FR_SUFFIX= ".fr.tok"


def separate_identification(line):
    tree = etree.fromstring(line)
    line_count = tree.attrib["COUNT"]
    name = tree.attrib["NAME"]
    lang = tree.attrib["LANGUAGE"]
    return line_count, name, lang


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("-p","--file-pattern", nargs='+', required=True, help="The base file name pattern where the files with suffixes {%s,%s,%s} are"%(ID_SUFFIX, EN_SUFFIX, FR_SUFFIX))
    p.add_argument("--output-location",default="/tmp/")
    p.add_argument("--output-suffix",default="-out.json")
    return p.parse_args()


def get_speakers_lines_from_file(pattern):
    filename = pattern + ID_SUFFIX
    logging.info("Running speaker extraction from "+filename)
    speakers = {}
    with open(filename) as f:
        for line in f:
            line_count, name, lang = separate_identification(line)
            if name not in speakers:
                speakers[name] = {}
                speakers[name]["EN"] = []
                speakers[name]["FR"] = []
            speakers[name][lang].append(line_count)
    return speakers


if __name__ == '__main__':
    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    for pattern in args.file_pattern:
        logging.info("Running speaker extraction from pattern "+pattern)
        speakers = get_speakers_lines_from_file(pattern)
        logging.info("Found " + str(len(speakers)) + " speakers")
        output = args.output_location + pattern.split("/")[-1] + args.output_suffix
        logging.info("Outputting speakers to "+output)
        with open(output,'w') as out:
            json.dump(speakers,out, sort_keys=True, indent=4, separators=(',', ': '))

