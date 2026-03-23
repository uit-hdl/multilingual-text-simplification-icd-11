"""
Experiments with multilingual text paraphrasing
using a PRISM model: https://github.com/thompsonb/prism/tree/master/paraphrase_generation
"""

# How to install & run

# The dependencies need downgraded version of pip, so first creating venv and using lower version of pip:

# python -m venv fairseq_env
# source fairseq_env/bin/activate
# pip install "pip<24.1"
# pip install fairseq
# pip install sentencepiece

# dict.tgt.txt is given
# data/prism_test.src.en: preprocessed text will be here
# data/prism_preprocessed: files generated during preprocessing will be put here (empty it for a new test run)

# preprocessing:
# fairseq-preprocess --source-lang en --target-lang en  \
#     --joined-dictionary  --srcdict models/prism/dict.tgt.txt \
#     --trainpref  data/prism_test.src  --validpref data/prism_test.src  --testpref data/prism_test.src --destdir data/prism_preprocessed

# paraphrasing:
# python prism/paraphrase_generation/generate_paraphrases.py data/prism_preprocessed --batch-size 8 \
#    --prefix-size 1 \
#    --path models/prism/checkpoint.pt \
#    --prism_a 0.006 --prism_b 4 > results/prism_test_output.txt

# full pipeline:
# python src/prism_model_experiments.py (from fairseq-env and root folder)

import os
import sys
import shutil
import subprocess

sys.path.append("/Users/olga/pycharm/multilingual_chatbot_trusting/eval_utils")

from text_simplification_evaluation import *
import sentencepiece as spm

lang = 'en'

sp = spm.SentencePieceProcessor()
sp.Load('models/prism/spm.model')

# original = '''Schizophrenia is characterised by disturbances in multiple mental modalities, including thinking (e.g., delusions, disorganisation in the form of thought), perception (e.g., hallucinations), self-experience (e.g., the experience that one's feelings, impulses, thoughts, or behaviour are under the control of an external force), cognition (e.g., impaired attention, verbal memory, and social cognition), volition (e.g., loss of motivation), affect (e.g., blunted emotional expression), and behaviour (e.g., behaviour that appears bizarre or purposeless, unpredictable or inappropriate emotional responses that interfere with the organisation of behaviour).'''

icd_texts_paths = 'results/parallel_icd_texts_6A20.tsv'

original = get_text(icd_texts_paths,
                  ("language", "en"),
                  ("code", "6A20"),
                  output_col="original_text") + ' ' +\
           get_text(icd_texts_paths,
                  ("language", "en"),
                  ("code", "6A20.0"),
                  output_col="original_text") + ' ' +\
           get_text(icd_texts_paths,
                  ("language", "en"),
                  ("code", "6A20.1"),
                  output_col="original_text") + ' ' +\
           get_text(icd_texts_paths,
                  ("language", "en"),
                  ("code", "6A20.2"),
                  output_col="original_text")

sents = [original]
sp_sents = [' '.join(sp.EncodeAsPieces(sent)) for sent in sents]

with open(f'data/prism_test.src.{lang}', 'wt') as fout:
    for sent in sp_sents:
        fout.write(sent + '\n')

# remove existing folder with preprocessed files
if os.path.exists('data/prism_preprocessed'):
    shutil.rmtree('data/prism_preprocessed', ignore_errors=True)
    os.makedirs('data/prism_preprocessed')

# run preprocessing and paraphrasing
subprocess.run(["bash", "src/run_prism_paraphrasing.sh"])

# check the result
simplified = ''
with open('results/prism_test_output.txt', 'r') as f:
    text = f.readlines()
    for line in text:
        if line.startswith('H-'):
            result = line.split('\t')[2]
            simplified = sp.DecodePieces(result.split(' '))

print(f'original: {original}')
print(f'simplified: {simplified}')
