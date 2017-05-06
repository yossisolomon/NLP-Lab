#!/usr/bin/python

import argparse
import logging
import xml.etree.ElementTree as etree
import json
import matplotlib.pyplot as plt

ID_SUFFIX = ".id"
EN_SUFFIX = ".en.tok"
FR_SUFFIX = ".fr.tok"
EN_LINES_KEY = "EN_LINES"
FR_LINES_KEY = "FR_LINES"
EN_PERCENT_KEY = "EN_PERCENT"
FR_PERCENT_KEY = "FR_PERCENT"



def separate_identification(line):
    tree = etree.fromstring(line)
    line_count = tree.attrib["COUNT"]
    name = tree.attrib["NAME"]
    lang = tree.attrib["LANGUAGE"]
    return line_count, name, lang


def add_speakers_lines_from_id_file(filename,speakers):
    logging.info("Running speaker extraction from "+filename)
    with open(filename) as f:
        for line in f:
            line_count, name, lang = separate_identification(line)
            if name not in speakers:
                speakers[name] = {}
                speakers[name][EN_LINES_KEY] = []
                speakers[name][FR_LINES_KEY] = []
            speakers[name][lang+"_LINES"].append(line_count)
    logging.info("Found " + str(len(speakers)) + " speakers")
    return speakers


def output_speakers_json(output_location, speakers):
    output = output_location
    logging.info("Outputting speakers to " + output)
    with open(output, 'w') as out:
        json.dump(speakers, out, sort_keys=True, indent=4, separators=(',', ': '))


def add_speakers_stats(speakers):
    for speaker in speakers:
        en_lines = len(speakers[speaker][EN_LINES_KEY])
        fr_lines = len(speakers[speaker][FR_LINES_KEY])
        tot_lines = float(en_lines + fr_lines)
        speakers[speaker][EN_PERCENT_KEY] = en_lines / tot_lines
        speakers[speaker][FR_PERCENT_KEY] = fr_lines / tot_lines


def create_minimum_lines_speakers_graph(speakers):
    x = [speakers[s][EN_PERCENT_KEY] for s in speakers]
    x.sort()
    # the histogram of the data
    plt.hist(x)
    plt.xlabel(EN_PERCENT_KEY)
    plt.ylabel('Speakers')
    plt.title('Histogram of EN Line Percentage')
    plt.grid(True)

    plt.show()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("-p","--file-pattern", nargs='+', required=True, help="The base file name pattern where the files with suffixes {%s,%s,%s} are"%(ID_SUFFIX, EN_SUFFIX, FR_SUFFIX))
    p.add_argument("--output-location",default="/tmp/speakers-out.json")
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    speakers = {}
    for pattern in args.file_pattern:
        logging.info("Running speaker extraction from pattern "+pattern)
        add_speakers_lines_from_id_file(pattern + ID_SUFFIX, speakers)
    logging.info("Found " + str(len(speakers)) + " total speakers")
    add_speakers_stats(speakers)
    output_speakers_json(args.output_location, speakers)
    create_minimum_lines_speakers_graph(speakers)



