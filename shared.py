import logging
import json


ID_SUFFIX = ".id"
EN_SUFFIX = ".en.tok"
FR_SUFFIX = ".fr.tok"
EN_LINES_KEY = "EN_LINES"
EN_NON_NATIVE_LINES_KEY = "NON_NATIVE_LINES"
FR_LINES_KEY = "FR_LINES"
EN_PERCENT_KEY = "EN_PERCENT"
FR_PERCENT_KEY = "FR_PERCENT"
CHUNK_FILENAME_PREFIX = "{}-chunk-size-{}"
COUNTS_SUFFIX = '-counts.json'


def set_logging(debug):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def load_lines_json(output_location):
    file = output_location + "lines-out.json"
    logging.info("Loading lines from " + file)
    lines = {}
    with open(file) as f:
        lines = json.load(f)
    return lines


def lines_dict_to_words_dict(lines):
    logging.info("Generating list of words from corpus")
    words = {}
    for class_key in lines.keys():
        words[class_key] = []
        for l in lines[class_key]:
            split_line = l.split()
            words[class_key].extend(split_line)
    return words
