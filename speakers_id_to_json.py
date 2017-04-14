#!/usr/bin/python

import argparse
import logging
import xml.etree.ElementTree as etree
import json


ID_SUFFIX=".id"
EN_SUFFIX=".en.tok"
Fr_SUFFIX=".fr.tok"


def separate_identification(line):
    tree = etree.fromstring(line)
    line_count = tree.attrib["COUNT"]
    name = tree.attrib["NAME"]
    lang = tree.attrib["LANGUAGE"]
    return line_count, name, lang


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("-p","--file-pattern",nargs='+',required=True)
    p.add_argument("-o","--output-location",default="/tmp/")
    p.add_argument("-o","--output-suffix",default="-out.json")
    return p.parse_args()


def get_speakers_lines_from_file(pattern):
    speakers = {}
    with open(pattern + ID_SUFFIX) as f:
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

    for pattern in args.file_pattern:
        logging.debug("Running for pattern "+pattern)
        speakers = get_speakers_lines_from_file(pattern)
        output = args.output_location + pattern + args.output_suffix
        logging.debug("Outputting speakers to "+output)
        with open(output,'w') as out:
            json.dump(speakers,out, sort_keys=True, indent=4, separators=(',', ': '))

