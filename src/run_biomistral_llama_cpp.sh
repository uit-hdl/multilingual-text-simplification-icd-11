#!/bin/bash
# Description: Experiments with medical text simplification
#using a BioMistral model: https://huggingface.co/BioMistral

# In particular this quantized version (to run on CPU-only local machine):
# https://huggingface.co/MaziyarPanahi/BioMistral-7B-SLERP-GGUF/tree/main

# Download: BioMistral-7B-SLERP.Q4_K_M.gguf
# Models path: ../models/BioMistral/BioMistral-7B-SLERP.Q4_K_M.gguf

# llama.cpp folder should be located at ./multilingual_chatbot_trusting/

# git clone https://github.com/ggerganov/llama.cpp
# cd llama.cpp
# cmake -B build   # no -DGGML_CUDA=ON
# cmake --build build --config Release -j$(nproc)

cd ../llama.cpp

text="$1"
seed="$2"
icd_code="$3"
lang="$4"
language="$5"

#text="Schizophrenia is characterised by disturbances in multiple mental modalities, including thinking (e.g., delusions, disorganisation in the form of thought), perception (e.g., hallucinations), self-experience (e.g., the experience that one's feelings, impulses, thoughts, or behaviour are under the control of an external force), cognition (e.g., impaired attention, verbal memory, and social cognition), volition (e.g., loss of motivation), affect (e.g., blunted emotional expression), and behaviour (e.g., behaviour that appears bizarre or purposeless, unpredictable or inappropriate emotional responses that interfere with the organisation of behaviour). Psychomotor disturbances, including catatonia, may be present. Persistent delusions, persistent hallucinations, thought disorder, and experiences of influence, passivity, or control are considered core symptoms. Symptoms must have persisted for at least one month in order for a diagnosis of schizophrenia to be assigned. The symptoms are not a manifestation of another health condition (e.g., a brain tumour) and are not due to the effect of a substance or medication on the central nervous system (e.g., corticosteroids), including withdrawal (e.g., alcohol withdrawal)."

#prompt="Rewrite this medical definition for a layman person.
#Keep it as close to the original meaning as possible, just use simpler words and syntactic constructions.
#
#medical definition:
#${text}
#
#simplified text:
#"

#prompt="Überarbeite diese medizinische Definition für Laien.
#Halte dich so nah wie möglich an die ursprüngliche Bedeutung, verwende aber einfachere Wörter und Satzkonstruktionen.
#
#Medizinische Definition:
#${text}
#
#Vereinfachter Text:
#"

prompt="Réécrivez cette définition médicale pour un profane.
Restez aussi proche que possible du sens original, en utilisant simplement des mots et des constructions syntaxiques plus simples.

Définition médicale :
${text}

Texte simplifié :
"

# -ngl 0 (no GPU layers)
# -m path to the downloaded model
# -t for CPU threads
# -p prompt
# -n number of tokens to generate
./build/bin/llama-completion \
  -m ../models/BioMistral/BioMistral-7B-SLERP.Q4_K_M.gguf \
  -ngl 0 \
  -t 8 \
  --prompt "$prompt" \
  --temp 0.3 \
  --top_p 0.8 \
  --seed $seed \
  -no-cnv \
  -n 200 > ../results/${lang}/${icd_code}/biomistral_output.txt
