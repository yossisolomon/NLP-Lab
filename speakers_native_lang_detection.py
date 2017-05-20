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


class NativeSpeakerSeparator:
    def __init__(self, threshold):
        self.threshold = threshold

    def is_native_english_speaker(self, speaker):
        return speaker[FR_PERCENT_KEY] < self.threshold

    def __str__(self):
        return "Threshold=" + str(self.threshold * 100) + " as max % of FR lines"


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


def load_speakers_json(output_location):
    file = output_location
    logging.info("Loading speakers from " + file)
    speakers = {}
    with open(file) as f:
        speakers = json.load(f)
    return speakers


def add_speakers_stats(speakers):
    for speaker in speakers:
        en_lines = len(speakers[speaker][EN_LINES_KEY])
        fr_lines = len(speakers[speaker][FR_LINES_KEY])
        tot_lines = float(en_lines + fr_lines)
        speakers[speaker][EN_PERCENT_KEY] = en_lines / tot_lines
        speakers[speaker][FR_PERCENT_KEY] = fr_lines / tot_lines


def create_minimum_lines_speakers_graph(speakers):
    title = 'Histogram of EN Line Percentage'
    logging.info("Creating " + title)
    x = [speakers[s][EN_PERCENT_KEY] for s in speakers]
    x.sort()
    # the histogram of the data
    plt.hist(x)
    plt.xlabel(EN_PERCENT_KEY)
    plt.ylabel('Speakers')
    plt.title(title)
    plt.grid(True)
    logging.info("Showing " + title)
    plt.show()


def get_speakers_stats_from_id_file(file_patterns):
    speakers = {}
    for pattern in file_patterns:
        logging.info("Running speaker extraction from pattern " + pattern)
        add_speakers_lines_from_id_file(pattern + ID_SUFFIX, speakers)
    logging.info("Found " + str(len(speakers)) + " total speakers")
    add_speakers_stats(speakers)
    return speakers


def separate_lines_by_lang(speakers, separator):
    en_native_lines = []
    en_non_native_lines = []
    fr_native_lines = []
    for speaker in speakers.keys():
        if separator.is_native_english_speaker(speakers[speaker]):
            en_native_lines.extend(speakers[speaker][EN_LINES_KEY])
        else:
            en_non_native_lines.extend(speakers[speaker][EN_LINES_KEY])
            fr_native_lines.extend(speakers[speaker][FR_LINES_KEY])
    logging.info("By check - " + str(separator) + " we got:\n"
                 + str(len(en_native_lines)) + " English native lines, "
                 + str(len(en_non_native_lines)) + " English non-native lines, and "
                 + str(len(fr_native_lines)) + " French lines")
    return en_native_lines, en_non_native_lines, fr_native_lines


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("-p","--file-patterns", nargs='+', required=True, help="The base file name pattern where the files with suffixes {%s,%s,%s} are"%(ID_SUFFIX, EN_SUFFIX, FR_SUFFIX))
    p.add_argument("--output-location",default="/tmp/speakers-out.json")
    p.add_argument("--speaker-stats-from-file",action='store_true')
    p.add_argument("--show-graph",action='store_true')
    p.add_argument("-t","--threshold",type=float,default=0.1)
    return p.parse_args()


def set_logging(debug):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def assert_no_duplicates(checked_list):
    full_len = len(checked_list)
    set_len = len(set(checked_list))
    msg = "full="+str(full_len)+" set="+str(set_len)
    assert (full_len - set_len == 0, msg)


if __name__ == '__main__':
    args = parse_args()
    set_logging(args.debug)

    speakers = {}
    if args.speaker_stats_from_file:
        speakers = load_speakers_json(args.output_location)
    else:
        speakers = get_speakers_stats_from_id_file(args.file_patterns)
        output_speakers_json(args.output_location, speakers)

    if args.show_graph:
        create_minimum_lines_speakers_graph(speakers)

    separator = NativeSpeakerSeparator(args.threshold)
    en_native_lines, en_non_native_lines, fr_native_lines = separate_lines_by_lang(speakers,separator)
    logging.info("Checking for line duplicates...")
    assert_no_duplicates(en_native_lines)
    assert_no_duplicates(en_non_native_lines)
    assert_no_duplicates(fr_native_lines)
    logging.info("All Good!")

    #TODO Add NLP part...
