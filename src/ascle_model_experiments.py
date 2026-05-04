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

icd_code = '6A20'
lang = 'fr'

# models we want to try out
ascle_models = ["li-lab/ascle-bigbird-pegasus-large-pubmed-elife-finetuned",
                "li-lab/ascle-bigbird-pegasus-large-pubmed-plos-finetuned",
                "li-lab/ascle-biobart-v2-base-elife-finetuned",
                "li-lab/ascle-biobart-v2-base-plos-finetuned",
                "li-lab/ascle-bart-large-PLOS-finetuned",
                "li-lab/ascle-bart-large-elife-finetuned"]


# open ICD text
icd_texts_paths = f'../results/parallel_icd_texts/parallel_icd_texts_{icd_code}.tsv'

original = 'La schizophrénie se caractérise par des perturbations de multiples modalités'

# original = get_text(icd_texts_paths,
#                   ("language", lang),
#                   ("code", f"{icd_code}"),
#                   output_col="original_text") + ' ' +\
#            get_text(icd_texts_paths,
#                   ("language", lang),
#                   ("code", f"{icd_code}.0"),
#                   output_col="original_text") + ' ' +\
#            get_text(icd_texts_paths,
#                   ("language", lang),
#                   ("code", f"{icd_code}.1"),
#                   output_col="original_text") + ' ' +\
#            get_text(icd_texts_paths,
#                   ("language", lang),
#                   ("code", f"{icd_code}.2"),
#                   output_col="original_text")

results = []
results_path = f'../results/{lang}/{icd_code}/ascle_model_results.tsv'

for model in ascle_models:
    med.update_and_delete_main_record(original)
    simplified = med.get_layman_text(model, min_length=50, max_length=200)

    print(simplified)

    row = build_metrics_row(
        model=model,
        original=original,
        simplified=simplified
    )

    results.append(row)

write_results_tsv(results, results_path)
