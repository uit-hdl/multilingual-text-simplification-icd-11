#!/bin/bash

lang="$1"

# run preprocessing
fairseq-preprocess --source-lang ${lang} --target-lang ${lang}  \
    --joined-dictionary  --srcdict models/prism/dict.tgt.txt \
    --trainpref  data/prism_test.src  --validpref data/prism_test.src  --testpref data/prism_test.src --destdir data/prism_preprocessed

# perform paraphrasing
python prism/paraphrase_generation/generate_paraphrases.py data/prism_preprocessed --batch-size 8 \
   --prefix-size 1 \
   --path models/prism/checkpoint.pt \
   --prism_a 0.006 --prism_b 4 > results/${lang}/6A20/prism_test_output.txt