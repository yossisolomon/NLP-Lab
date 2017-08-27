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
