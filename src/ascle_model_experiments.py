"""
Experiments with medical text simplification
using Ascle models: https://github.com/Yale-LILY/Ascle
"""

from eval_utils.text_simplification_evaluation import *
import warnings
import sys
import os

warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.append(os.path.abspath("../models/Ascle"))

from Ascle import Ascle


# create Ascle instance
med = Ascle()

# models we want to try out
ascle_models = ["li-lab/ascle-bigbird-pegasus-large-pubmed-elife-finetuned",
                "li-lab/ascle-bigbird-pegasus-large-pubmed-plos-finetuned",
                "li-lab/ascle-biobart-v2-base-elife-finetuned",
                "li-lab/ascle-biobart-v2-base-plos-finetuned",
                "li-lab/ascle-bart-large-PLOS-finetuned",
                "li-lab/ascle-bart-large-elife-finetuned"]


# open ICD text
icd_texts_paths = '../results/parallel_icd_texts_6A20.tsv'

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

results = []
results_path = '../results/ascle_model_results.tsv'

for model in ascle_models:
    med.update_and_delete_main_record(original)
    simplified = med.get_layman_text(model, min_length=20, max_length=80)

    row = build_metrics_row(
        model=model,
        original=original,
        simplified=simplified
    )

    results.append(row)

write_results_tsv(results, results_path)
