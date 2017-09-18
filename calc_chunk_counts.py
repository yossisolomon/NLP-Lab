#!/usr/bin/python

import argparse
from random import shuffle
from collections import Counter
import itertools
import nltk

from shared import *
from en_function_words import FUNCTION_WORDS


def lines_to_word_chunks(class_lines, chunk_size, to_shuffle=False):
    curr_chunk = []
    chunks = []
    if to_shuffle:
        shuffle(class_lines)
    for l in class_lines:
        split_line = l.split()
        curr_chunk.extend(split_line)
        if len(curr_chunk) >= chunk_size:
            chunks.append(curr_chunk)
            curr_chunk = []
    return chunks


# freq list of a chunk
def get_chunk_counts(words, counters):
    counts = []
    for c in counters:
        if len(c) == 1:
            counts.extend(c[0](words))
        else:
            counts.extend(c[0](words,c[1]))
    return counts


def get_pos_trigram_counts(words, pos_trigrams):
    c = Counter(nltk.trigrams(words))
    return [c[t] for t in pos_trigrams]


def get_func_word_counts(words):
    c = Counter(words)
    fw_words_counts = map(lambda fw: c[fw], FUNCTION_WORDS)
    assert len(fw_words_counts) == len(FUNCTION_WORDS), "{} not {}".format(str(len(fw_words_counts)),
                                                                           str(len(FUNCTION_WORDS)))
    return fw_words_counts


def words_to_most_common_pos_trigrams(words, top=3000):
    logging.info("Calculating %d most common POS Trigrams in corpus", top)
    c = Counter(nltk.trigrams(words))
    return [t[0] for t in c.most_common(top)]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("-j","--lines-json-location",default="/tmp/")
    p.add_argument("--output-location",default="/tmp/")
    p.add_argument("--function-word-counts",action='store_true')
    p.add_argument("--pos-counts",action='store_true')
    p.add_argument("-c","--chunk-size",type=int,default=1000)
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    set_logging(args.debug)

    lines = load_lines_json(args.lines_json_location)

    counters = []
    if args.pos_counts:
        words = lines_dict_to_words_dict(lines)
        logging.info("Generating POS counts from words")
        pos_trigrams = words_to_most_common_pos_trigrams(itertools.chain.from_iterable(words.values()))
        logging.debug(pos_trigrams)
        counters.append([get_pos_trigram_counts, pos_trigrams])

    if args.function_word_counts:
        counters.append([get_func_word_counts])

    assert len(counters) > 0, "No counter selected for chunks, see help for flags"

    for key in [EN_LINES_KEY, EN_NON_NATIVE_LINES_KEY, FR_LINES_KEY]:
        logging.info("Generating " + key + " chunks of size=" + str(args.chunk_size))
        chunks = lines_to_word_chunks(lines[key], args.chunk_size)
        logging.info("Analyzing chunks")
        chunks_counts = [get_chunk_counts(chunk, counters) for chunk in chunks]
        filename = args.output_location + CHUNK_FILENAME_PREFIX.format(key,str(args.chunk_size)) + COUNTS_SUFFIX
        logging.info("Writing chunks' counts to %s", filename)
        with open(filename, 'w') as f:
            json.dump(chunks_counts, f)
        logging.info("Done writing chunks' counts to %s", filename)
