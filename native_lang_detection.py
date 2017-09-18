#!/usr/bin/python

import argparse
import numpy as np
from random import shuffle
from sklearn.cross_validation import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier

from shared import *


def load_chunks_by_class(filename, sample_size):
    logging.info("Loading chunks from %s with sample amount of %d samples", filename, sample_size)
    with open(filename) as f:
        chunks = json.load(f)
        assert len(chunks) >= sample_size, filename + " has insufficient samples! It has only = " + str(len(chunks))
        chunks = chunks[:sample_size]
        return chunks


def score_cross_validated(chunks_list, classes_list):
    data = np.concatenate(chunks_list)
    target = np.concatenate(classes_list)
    clf = RandomForestClassifier(n_estimators=20)
    cv = StratifiedKFold(target, n_folds=10)
    # Valid scoring options are ['accuracy', 'adjusted_rand_score', 'average_precision', 'f1', 'log_loss', 'mean_squared_error', 'precision', 'r2', 'recall', 'roc_auc']
    score = cross_val_score(clf, data, target, cv=cv, scoring='accuracy')
    logging.info(score)
    logging.info("Average score = %f", np.mean(score, dtype=np.float64))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("--input-location",default="/tmp/")
    p.add_argument("-c","--chunk-size",type=int,default=1000)
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    set_logging(args.debug)

    chunks_by_class = {}
    for k in [EN_LINES_KEY, EN_NON_NATIVE_LINES_KEY, FR_LINES_KEY]:
        filename = args.input_location + CHUNK_FILENAME_PREFIX.format(k, str(args.chunk_size)) + COUNTS_SUFFIX
        logging.info("Loading chunks from %s", filename)
        chunks_by_class[k] = json.load(open(filename))

    sample_size = min([len(c) for c in chunks_by_class.values()])
    logging.info("Using sample amount of %d samples (min of all classes)", sample_size)

    i = 0
    for k in [EN_LINES_KEY, EN_NON_NATIVE_LINES_KEY, FR_LINES_KEY]:
        # Shuffle chunks used for better lexical diversity
        shuffle(chunks_by_class[k])
        # Use only sample_size chunks
        chunks_by_class[k] = chunks_by_class[k][:sample_size]
        # counts to frequencies
        chunks_by_class[k] = map(lambda chunk: [count / float(args.chunk_size) for count in chunk], chunks_by_class[k])
        # Per class - normalized frequency vector as input, labelling for class
        chunks_by_class[k] = (np.asarray(chunks_by_class[k], np.float), np.repeat(i, sample_size))
        i += 1

    keys = [EN_LINES_KEY, FR_LINES_KEY]
    logging.info("Scoring %s",str(keys))
    score_cross_validated([chunks_by_class[k][0] for k in keys], [chunks_by_class[k][1] for k in keys])

    keys = [FR_LINES_KEY, EN_NON_NATIVE_LINES_KEY]
    logging.info("Scoring %s",str(keys))
    score_cross_validated([chunks_by_class[k][0] for k in keys], [chunks_by_class[k][1] for k in keys])

    keys = [EN_LINES_KEY, EN_NON_NATIVE_LINES_KEY]
    logging.info("Scoring %s",str(keys))
    score_cross_validated([chunks_by_class[k][0] for k in keys], [chunks_by_class[k][1] for k in keys])

    keys = [EN_LINES_KEY, EN_NON_NATIVE_LINES_KEY, FR_LINES_KEY]
    logging.info("Scoring %s",str(keys))
    score_cross_validated([chunks_by_class[k][0] for k in keys], [chunks_by_class[k][1] for k in keys])
