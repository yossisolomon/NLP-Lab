#!/usr/bin/python

import argparse
import xml.etree.ElementTree as etree
import matplotlib.pyplot as plt

from shared import *


def separate_identification(line):
    tree = etree.fromstring(line)
    line_count = tree.attrib["COUNT"]
    name = tree.attrib["NAME"]
    lang = tree.attrib["LANGUAGE"]
    return line_count, name, lang


def add_speakers_lines_from_id_file(filename):
    speakers = {}
    logging.info("Running speaker extraction from "+filename)
    logging.info("Loading IDs from %s", filename)
    id_file_as_list = open(filename).read().splitlines()
    logging.info("Done loading IDs from %s", filename)
    for line in id_file_as_list:
        line_count, name, lang = separate_identification(line)
        if name not in speakers:
            speakers[name] = {}
            speakers[name][EN_LINES_KEY] = []
            speakers[name][FR_LINES_KEY] = []
        speakers[name][lang+"_LINES"].append(line_count)
    logging.info("Found %d speakers", len(speakers))
    return speakers


def output_speakers_json(output_location, speakers):
    output = output_location + "speakers-out.json"
    logging.info("Outputting speakers to " + output)
    with open(output, 'w') as out:
        json.dump(speakers, out, sort_keys=True, indent=4, separators=(',', ': '))


def output_lines_json(output_location, lines):
    output = output_location + "lines-out.json"
    logging.info("Outputting lines to %s", output)
    with open(output, 'w') as out:
        json.dump(lines, out, indent=4, separators=(',', ': '))


def load_speakers_json(output_location):
    file = output_location + "speakers-out.json"
    logging.info("Loading speakers from " + file)
    return json.load(open(file))


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


def get_speakers_stats_from_id_file(file_pattern):
    speakers = add_speakers_lines_from_id_file(file_pattern + ID_SUFFIX)
    logging.info("Found " + str(len(speakers)) + " total speakers")
    add_speakers_stats(speakers)
    return speakers


def separate_lines_by_lang(speakers, threshold):
    en_native_lines = []
    en_non_native_lines = []
    en_translated_lines = []
    for speaker in speakers.keys():
        # Take all fully english speakers as native English Speakers
        if speakers[speaker][EN_PERCENT_KEY] == 1.0:
            en_native_lines.extend(speakers[speaker][EN_LINES_KEY])
        # Take all those who spoke above a threshold in French to be Non-Native English Speakers
        elif speakers[speaker][FR_PERCENT_KEY] >= threshold:
            en_non_native_lines.extend(speakers[speaker][EN_LINES_KEY])
        # Take all translated texts from English to French as Translated English
        en_translated_lines.extend(speakers[speaker][FR_LINES_KEY])
    logging.info("""We got:
                 %d English native lines;
                 %d English non-native lines (Threshold = %d as min percentageof lines spoken in French);
                 %d Translated English (from French) lines""",
                 len(en_native_lines),
                 len(en_non_native_lines), threshold * 100,
                 len(en_translated_lines))
    return en_native_lines, en_non_native_lines, en_translated_lines


def assert_no_duplicates(checked_list):
    full_len = len(checked_list)
    set_len = len(set(checked_list))
    msg = "full="+str(full_len)+" set="+str(set_len)
    assert full_len - set_len == 0, msg


def check_class_list(class_list):
    assert_no_duplicates(class_list)
    assert len(class_list) > 0, "Class list is empty..."


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("-p","--file-pattern", required=True, help="The base file name pattern where the files with suffixes {%s,%s,%s} are"%(ID_SUFFIX, EN_SUFFIX, FR_SUFFIX))
    p.add_argument("--output-location",default="/tmp/")
    p.add_argument("--speaker-stats-from-file",action='store_true')
    p.add_argument("--show-graph",action='store_true')
    p.add_argument("-t","--threshold",type=float,default=0.5, choices=[x/10.0 for x in xrange(0, 10, 1)])
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    set_logging(args.debug)

    speakers = {}
    if args.speaker_stats_from_file:
        speakers = load_speakers_json(args.output_location)
    else:
        speakers = get_speakers_stats_from_id_file(args.file_pattern)
        output_speakers_json(args.output_location, speakers)

    if args.show_graph:
        create_minimum_lines_speakers_graph(speakers)

    en_native_line_nums, en_non_native_line_nums, en_translated_line_nums = separate_lines_by_lang(speakers, args.threshold)

    en_native_line_nums = map(lambda i: int(i), en_native_line_nums)
    en_non_native_line_nums = map(lambda i: int(i), en_non_native_line_nums)
    en_translated_line_nums = map(lambda i: int(i), en_translated_line_nums)

    logging.info("Checking for line class list problems...")
    check_class_list(en_native_line_nums)
    check_class_list(en_non_native_line_nums)
    check_class_list(en_translated_line_nums)
    logging.info("All Good!")

    lines = {
        EN_LINES_KEY: [],
        EN_NON_NATIVE_LINES_KEY: [],
        FR_LINES_KEY: []
    }
    f = args.file_pattern + EN_SUFFIX
    logging.info("Loading lines from %s", f)
    lines_file_as_list = open(f).read().splitlines()
    logging.info("Done loading lines from %s", f)

    logging.info("Extracting %s", EN_LINES_KEY)
    lines[EN_LINES_KEY] = [lines_file_as_list[i - 1] for i in en_native_line_nums]

    logging.info("Extracting %s", EN_NON_NATIVE_LINES_KEY)
    lines[EN_NON_NATIVE_LINES_KEY] = [lines_file_as_list[i - 1] for i in en_non_native_line_nums]

    logging.info("Extracting %s", FR_LINES_KEY)
    lines[FR_LINES_KEY] = [lines_file_as_list[i - 1] for i in en_translated_line_nums]

    output_lines_json(args.output_location, lines)

