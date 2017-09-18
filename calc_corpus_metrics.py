#!/usr/bin/python

import argparse
import matplotlib.pyplot as plt
from collections import Counter
from random import shuffle

from shared import *
from en_idioms import IDIOMS
from en_cohesive_markers import COHESIVE_MARKERS
from en_pronouns import PRONOUNS


def calc_lexical_richness(words, token_count):
    res = {}
    for class_key, class_words in words.items():
        shuffle(class_words)
        c = Counter(class_words[:token_count])
        rare_words_cnt = 0
        for cnt in c.values():
            if cnt == 1:
                rare_words_cnt += 1
        res[class_key] = rare_words_cnt
        logging.info("Lexical richness for class %s = %f", class_key, float(rare_words_cnt) / token_count)
    return res


def calc_collocations(words, token_count):
    res = {}
    for class_key, class_words in words.items():
        collocation_count = 0
        super_string = " ".join(class_words[:token_count])
        for i in IDIOMS:
            try:
                collocation_count += super_string.count(i)
            except UnicodeDecodeError:
                pass
        res[class_key] = collocation_count
        logging.info("Collocation metric for class %s = %f", class_key, float(collocation_count) / token_count)
    return res


def calc_cohesive_markers(words, token_count):
    res = {}
    for class_key, class_words in words.items():
        cohesive_markers_used = 0
        super_string = " ".join(class_words[:token_count])
        for m in COHESIVE_MARKERS:
            try:
                cohesive_markers_used += super_string.count(m)
            except UnicodeDecodeError:
                pass
        res[class_key] = cohesive_markers_used
        logging.info("Cohesive markers metric for class %s = %f", class_key, float(cohesive_markers_used) / token_count)
    return res


def calc_personal_pronouns(words, token_count):
    res = {}
    for class_key, class_words in words.items():
        shuffle(class_words)
        c = Counter(class_words[:token_count])
        pronoun_count = 0
        for p in PRONOUNS:
            pronoun_count += c[p]
        res[class_key] = pronoun_count
        logging.info("Personal pronouns metric for class %s = %f", class_key, float(pronoun_count) / token_count)
    return res


def plot_metrics(metrics_by_class, metric_keys):
    class_keys = metrics_by_class.keys()
    # Setting the positions and width for the bars
    pos = list(range(len(metric_keys)))
    width = 0.25
    # Plotting the bars
    _, ax = plt.subplots(figsize=(10, 5))
    class_iter = 0
    colors = ['#EE3224', '#F78F1E', '#FFC222']
    # for key in normalized_results_by_class.keys():
    for key in class_keys:
        plt.bar([p + width * class_iter for p in pos],
                metrics_by_class[key],
                width,
                alpha=0.5,
                color=colors[class_iter])
        class_iter += 1

    # Set the y axis label
    ax.set_ylabel('zero-one scale normalized value')
    # Set the chart's title
    ax.set_title('L1-independent similarities analysis')
    # Set the position of the x ticks
    ax.set_xticks([p + 1.5 * width for p in pos])
    # Set the labels for the x ticks
    ax.set_xticklabels(metric_keys)
    # Setting the x-axis and y-axis limits
    plt.xlim(min(pos) - width, max(pos) + width * 4)
    plt.ylim([0.25, 0.45])
    # Adding the legend and showing the plot
    plt.legend(metrics_by_class.keys(), loc='upper left')
    plt.grid()
    plt.show()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d","--debug",action='store_true')
    p.add_argument("-j","--lines-json-location",default="/tmp/")
    p.add_argument("--lines-from-file",action='store_true', help="Bypasses the speaker separation part")
    p.add_argument("--show-graph",action='store_true')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    set_logging(args.debug)

    lines = load_lines_json(args.lines_json_location)

    words = lines_dict_to_words_dict(lines)

    metrics = {
        "Lexical richness": calc_lexical_richness,
        "Collocations": calc_collocations,
        "Cohesive markers": calc_cohesive_markers,
        "Personal pronouns": calc_personal_pronouns
    }
    min_token_count = min([len(l) for l in words.values()])
    logging.info("Token amount for metric calculations = %d", min_token_count)

    normalized_results_by_class = {key: list() for key in words.keys()}
    for metric, calc in metrics.items():
        logging.info("Generating the %s metric from words",metric)
        result = calc(words, min_token_count)
        res_sum = sum(result.values())
        for class_key, class_result in result.items():
            normalized_res = float(class_result)/res_sum
            logging.info("Normalized (total sum) for class %s = %f", class_key, normalized_res)
            normalized_results_by_class[class_key].append(normalized_res)

    if args.show_graph:
        plot_metrics(normalized_results_by_class,metrics.keys())
