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

    # words, unique_words, ttr, mtld, hdd
    lex_richness_orig = get_lexical_richness(original)
    lex_richness_simp = get_lexical_richness(simplified)

    # standard metrics
    bleu = get_bleu(original, simplified)
    rouge = get_rouge(original, simplified)
    bert_score = get_bert_score(original, simplified)

    # readability metrics
    lix = get_lix_score(simplified)
    readability = get_readability_metrics(simplified)

    row = build_metrics_row(
        model=model,
        original=original,
        simplified=simplified,
        orig_word_count=lex_richness_orig['words'], orig_unique_words=lex_richness_orig['unique_words'], orig_ttr=lex_richness_orig['ttr'], orig_mtld=lex_richness_orig['mtld'], orig_hdd=lex_richness_orig['hdd'],
        simp_word_count=lex_richness_simp['words'], simp_unique_words=lex_richness_simp['unique_words'], simp_ttr=lex_richness_simp['ttr'], simp_mtld=lex_richness_simp['mtld'], simp_hdd=lex_richness_simp['hdd'],
        bleu=bleu['bleu'],
        rouge1_f1=rouge['rouge1']['f1'],
        rougel_f1=rouge['rougeL']['f1'],
        bert=bert_score,
        lix=lix,
        flesch_reading_ease=readability['flesch_reading_ease'],
        flesch_kincaid_grade=readability['flesch_kincaid_grade'],
        smog_index=readability['smog_index'],
        gunning_fog=readability['gunning_fog'],
        coleman_liau_index=readability['coleman_liau_index'],
        automated_readability_index=readability['automated_readability_index'],
        dale_chall_readability_score=readability['dale_chall_readability_score'],
    )

    results.append(row)

write_results_tsv(results, results_path)


# find the best results
results = find_best_model(results_path)

print("Win counts:")
for model, wins in sorted(results["win_counts"].items(), key=lambda x: -x[1]):
    print(f"  {model}: {wins} wins")

print(f"\nBest model: {results['best_model']}")

print(results['metric_winners'])
