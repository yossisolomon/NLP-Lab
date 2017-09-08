#!/bin/bash

for i in 0.1 0.2 0.3 0.4 0.5 ; do
    python corpus_to_chunks.py -p hansard.EN-FR/hansard/train --speaker-stats-from-file -t $i && python native_lang_detection.py ;
done
