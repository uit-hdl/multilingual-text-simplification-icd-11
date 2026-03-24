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
