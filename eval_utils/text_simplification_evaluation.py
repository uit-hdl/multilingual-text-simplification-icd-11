"""
Evaluation metrics for text simplification task
and readability metrics (mostly for English)
"""

from bert_score import score
from rouge_score import rouge_scorer
from lexicalrichness import LexicalRichness
import statistics
import sacrebleu
import textstat
import csv


# get the ICD text based on filters (language, ICD code)
def get_text(tsv_path: str, filter1: tuple, filter2: tuple, output_col: str) -> str:
    f = open(tsv_path, "r", encoding="utf-8")
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        if row[filter1[0]] == filter1[1] and row[filter2[0]] == filter2[1]:
            f.close()
            return row[output_col]
    f.close()
    return ''


def get_lexical_richness(simplified: str) -> dict:
    """Lexical richness of the simplified text alone (no reference needed)."""
    lex = LexicalRichness(simplified)
    return {
        "words":       lex.words,           # total word count
        "unique_words": lex.terms,          # unique word count
        "ttr":         round(lex.ttr, 4),   # Type-Token Ratio (unique/total); lower = better
        "mattr": lex.mattr(window_size=min(50, lex.words)),  # because we are using short texts, we set a smaller window
        "mtld":        round(lex.mtld(threshold=0.72), 4),  # robust TTR alternative; lower = better
        # "hdd":         round(lex.hdd(draws=42), 4),         # HD-D diversity index; lower = better
    }


def get_bleu(original: str, simplified: str) -> dict:   # Higher = better
    """BLEU score: how much the simplified text matches the original as reference."""
    result = sacrebleu.sentence_bleu(simplified, [original])
    return {
        "bleu": result.score,           # 0–100, higher = more similar to original
        "precisions": result.precisions  # n-gram precision breakdown
    }


def get_rouge(original: str, simplified: str) -> dict:  # Higher = better
    """ROUGE scores: overlap of unigrams (R1), bigrams (R2), and longest common subsequence (RL)."""
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
    scores = scorer.score(original, simplified)
    return {
        metric: {
            "precision": round(scores[metric].precision, 4),
            "recall":    round(scores[metric].recall, 4),
            "f1":        round(scores[metric].fmeasure, 4)
        }
        for metric in scores
    }


def get_bert_score(reference_texts, simplified_texts):  # Higher = better
    p, r, f1 = score(
        [simplified_texts],
        [reference_texts],
        lang="en",
        model_type="bert-base-multilingual-cased"
    )

    f1_score = f1[0].item()
    return f1_score


def get_lix_score(simplified_text):  # Lower = better
    return textstat.lix(simplified_text)


def get_rix_score(simplified_text):  # Lower = better
    return textstat.rix(simplified_text)


# readability metrics for English
def get_readability_metrics(simplified: str, lang='en') -> dict:
    textstat.set_lang(lang)
    return {
        "flesch_reading_ease":        textstat.flesch_reading_ease(simplified),        # Higher = better
        "flesch_kincaid_grade":       textstat.flesch_kincaid_grade(simplified),       # Lower = better
        "smog_index":                 textstat.smog_index(simplified),                 # Lower = better
        "gunning_fog":                textstat.gunning_fog(simplified),                 # Lower = better
        "coleman_liau_index":         textstat.coleman_liau_index(simplified),          # Lower = better
        "automated_readability_index": textstat.automated_readability_index(simplified),    # Lower = better
        "dale_chall_readability_score": textstat.dale_chall_readability_score(simplified),  # Lower = better
    }


def build_metrics_row(
    model: str,
    original: str,
    simplified: str
) -> dict:
    return {
        "model":                        model,
        "original_text":                original,
        "simplified_text":              simplified
    }


# write results into a TSV
def write_results_tsv(rows: list, output_path: str) -> None:
    with open(output_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


# read results file
def read_tsv_3cols(filepath):
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if '\t' in line:
                parts = line.rstrip('\n').split("\t")
                col1, col2, col3 = parts
                data.append((col1, col2, col3))
    return data
