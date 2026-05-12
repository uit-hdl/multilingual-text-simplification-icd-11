"""
Experiments with medical text simplification
using a BioMistral model: https://huggingface.co/BioMistral
"""

from eval_utils.text_simplification_evaluation import *
import subprocess
import re

icd_code = '6A20'
lang = 'fr'
language = 'French'

# open ICD text
icd_texts_paths = f'../results/parallel_icd_texts/parallel_icd_texts_{icd_code}.tsv'
biomistral_model = 'BioMistral-7B-SLERP.Q4_K_M.gguf'

original = get_text(icd_texts_paths,
                  ("language", lang),
                  ("code", f"{icd_code}"),
                  output_col="original_text") + ' ' +\
           get_text(icd_texts_paths,
                  ("language", lang),
                  ("code", f"{icd_code}.0"),
                  output_col="original_text") + ' ' +\
           get_text(icd_texts_paths,
                  ("language", lang),
                  ("code", f"{icd_code}.1"),
                  output_col="original_text") + ' ' +\
           get_text(icd_texts_paths,
                  ("language", lang),
                  ("code", f"{icd_code}.2"),
                  output_col="original_text")

# run the model using llama.cpp with the extracted ICD text
# we run this about 10 times, to see how the evaluation metrics change
# temperature was set by default to 0.8, we change it to 0.3

results = []
results_path = f'../results/{lang}/{icd_code}/biomistral_model_results.tsv'

for i in range(10):
    subprocess.run(["bash", "run_biomistral_llama_cpp.sh",
                    str(original), str(i), str(icd_code), str(lang), language])

    # open result file with the output
    with open(f"../results/{lang}/{icd_code}/biomistral_output.txt", "r") as f:
        content = f.read()
        # match = re.search(r"simplified text:[\r\n]*([^\r\n]+)[\r\n]*", content, re.DOTALL)
        # match = re.search(r"Vereinfachter Text:[\r\n]*([^\r\n]+)[\r\n]*", content, re.DOTALL)
        match = re.search(r"Texte simplifié :[\r\n]*([^\r\n]+)[\r\n]*", content, re.DOTALL)
        if match:
            model = f"run_{i}_" + biomistral_model
            print(model)

            simplified = match.group(1)
            simplified = simplified.replace(' [end of text]', '')
            print(simplified)

            row = build_metrics_row(
                model=model,
                original=original,
                simplified=simplified
            )

            results.append(row)
        else:
            print("NO MATCH")
            print(content)

write_results_tsv(results, results_path)
