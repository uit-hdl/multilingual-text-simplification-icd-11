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

HIGHER_IS_BETTER = {
    "flesch_reading_ease", "bleu", "bert",
    "rouge1_f1", "rougeL_f1"
}

LOWER_IS_BETTER = {
    "flesch_kincaid_grade", "smog_index", "gunning_fog", "coleman_liau_index",
    "automated_readability_index", "dale_chall_readability_score", "lix"
}

SKIP = {"original_text", "simplified_text", "model",
        "orig_word_count", "orig_unique_words",
        "orig_ttr", "orig_mltd", "orig_hdd",
        "simp_word_count", "simp_unique_words",
        "simp_ttr", "simp_mltd", "simp_hdd"}


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
        "mtld":        round(lex.mtld(threshold=0.72), 4),  # robust TTR alternative; lower = better
        "hdd":         round(lex.hdd(draws=42), 4),         # HD-D diversity index; lower = better
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


# readability metrics for English
def get_readability_metrics(simplified: str) -> dict:
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
    simplified: str,
    # original lexical
    orig_word_count: int,
    orig_unique_words: int,
    orig_ttr: float,
    orig_mtld: float,
    orig_hdd: float,
    # simplified lexical
    simp_word_count: int,
    simp_unique_words: int,
    simp_ttr: float,
    simp_mtld: float,
    simp_hdd: float,
    # standard reference-based
    bleu: float,
    rouge1_f1: float,
    rougel_f1: float,
    bert: float,
    # readability (simplified)
    lix: float,
    flesch_reading_ease: float,
    flesch_kincaid_grade: float,
    smog_index: float,
    gunning_fog: float,
    coleman_liau_index: float,
    automated_readability_index: float,
    dale_chall_readability_score: float,
) -> dict:
    return {
        "model":                        model,
        "original_text":                original,
        "simplified_text":              simplified,
        "orig_word_count":              orig_word_count,
        "orig_unique_words":            orig_unique_words,
        "orig_ttr":                     orig_ttr,
        "orig_mtld":                    orig_mtld,
        "orig_hdd":                     orig_hdd,
        "simp_word_count":              simp_word_count,
        "simp_unique_words":            simp_unique_words,
        "simp_ttr":                     simp_ttr,
        "simp_mtld":                    simp_mtld,
        "simp_hdd":                     simp_hdd,
        "bleu": bleu,
        "rouge1_f1": rouge1_f1,
        "rougeL_f1": rougel_f1,
        "bert": bert,
        "lix":                          lix,
        "flesch_reading_ease":          flesch_reading_ease,
        "flesch_kincaid_grade":         flesch_kincaid_grade,
        "smog_index":                   smog_index,
        "gunning_fog":                  gunning_fog,
        "coleman_liau_index":           coleman_liau_index,
        "automated_readability_index":  automated_readability_index,
        "dale_chall_readability_score": dale_chall_readability_score,
    }


# write results into a TSV
def write_results_tsv(rows: list, output_path: str) -> None:
    with open(output_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


# find best model
def find_best_model(tsv_path: str) -> dict:
    f = open(tsv_path, "r", encoding="utf-8")
    reader = csv.DictReader(f, delimiter="\t")
    rows = list(reader)
    f.close()

    win_counts = {row["model"]: 0 for row in rows}
    metric_winners = {}

    for col in rows[0].keys():
        if col in SKIP:
            continue
        if col not in HIGHER_IS_BETTER and col not in LOWER_IS_BETTER:
            continue

        if col in HIGHER_IS_BETTER:
            winner = max(rows, key=lambda r: float(r[col]))
        else:
            winner = min(rows, key=lambda r: float(r[col]))

        win_counts[winner["model"]] += 1
        metric_winners[col] = {"winner": winner["model"], "score": float(winner[col])}

    best_model = max(win_counts, key=win_counts.get)

    return {
        "win_counts":     win_counts,
        "best_model":     best_model,
        "metric_winners": metric_winners,
    }


# check mean and std of metric (for the same model but several runs)
def metric_stats(results, metric):
    values = [row[metric] for row in results]
    return {
        "mean": statistics.mean(values),
        "std": statistics.stdev(values)
    }
