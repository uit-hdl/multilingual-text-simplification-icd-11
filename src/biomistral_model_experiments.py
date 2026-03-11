"""
Experiments with medical text simplification
using a BioMistral model: https://huggingface.co/BioMistral
"""

from eval_utils.text_simplification_evaluation import *
import subprocess
import re

# open ICD text
icd_texts_paths = '../results/parallel_icd_texts_6A20.tsv'
biomistral_model = 'BioMistral-7B-SLERP.Q4_K_M.gguf'

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

# run the model using llama.cpp with the extracted ICD text
# let's run this about 10 times, to see how the evaluation metrics change
# temperature was set by default to 0.8

results = []
results_path = '../results/biomistral_model_results.tsv'

for i in range(10):
    subprocess.run(["bash", "run_biomistral_llama_cpp.sh", str(original), str(i)])

    # open result file with the output
    with open("../results/biomistral_output.txt", "r") as f:
        content = f.read()
        match = re.search(r"simplified text:\s*(.*?)(?:\s*\[end of text\]|$)", content, re.DOTALL)
        if match:
            model = f"run_{i}_" + biomistral_model
            print(model)

            simplified = match.group(1)
            print(simplified)

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
                orig_word_count=lex_richness_orig['words'], orig_unique_words=lex_richness_orig['unique_words'],
                orig_ttr=lex_richness_orig['ttr'], orig_mtld=lex_richness_orig['mtld'],
                orig_hdd=lex_richness_orig['hdd'],
                simp_word_count=lex_richness_simp['words'], simp_unique_words=lex_richness_simp['unique_words'],
                simp_ttr=lex_richness_simp['ttr'], simp_mtld=lex_richness_simp['mtld'],
                simp_hdd=lex_richness_simp['hdd'],
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
        else:
            print("NO MATCH")
            print(content)

write_results_tsv(results, results_path)

# check important stats
print("BLEU:", metric_stats(results, "bleu"))
print("ROUGE 1:", metric_stats(results, "rouge1_f1"))
print("ROUGE L:", metric_stats(results, "rougeL_f1"))
print("BERT:", metric_stats(results, "bert"))
