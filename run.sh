#!/bin/bash



file_pattern="hansard.EN-FR/committees/train"

echo Running Native, Non-Native, Translated NLP analysis

echo We are using the file pattern $file_pattern

echo

while true; do
    read -p $'Please make sure to close figure windows after looking/saving to allow continuation of the analysis, OK? [Yy/Nn] \n' yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes [Y/y] or no [N/n].";;
    esac
done

set -x

python corpus_to_files.py -p $file_pattern --show-graph
python calc_corpus_metrics.py --show-graph
python calc_chunk_counts.py --pos-counts --function-word-counts
python native_lang_detection.py
