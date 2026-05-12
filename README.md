# Evaluation of Multilingual Text Simplification for the Mental Health Domain: Exploring Small Language Models

Repository for the paper:

Olga Pelloni, Sandra Anna Just, Lars Ailo Bongo (2026). Evaluation of Multilingual Text Simplification for the Mental Health Domain: Exploring Small Language Models, BioNLP 2026.


## Data

Data comes from the [ICD-11 definitions](https://icd.who.int/browse/2025-01/mms/en#1683919430). We extracted the definitions using [ICD API](https://icd.who.int/icdapi) in English, German and French.


## Scripts

We tested our scripts using Python 3.8.18 and pip 25.0.1. PRISM model requires a fairseq package, for which one needs a separate environment with pip 23.0.1. Install required packages using ```fairseq_env_requirements.txt``` for the PRISM model and ```requirements.txt``` for the other models.

## Models

1. [PRISM](https://github.com/thompsonb/prism/tree/master/paraphrase_generation)
2. [Ascle models](https://github.com/Yale-LILY/Ascle)
3. [BioMistral 7B](https://huggingface.co/MaziyarPanahi/BioMistral-7B-SLERP-GGUF/tree/main) (using [llama.cpp](https://llama-cpp.com/))
