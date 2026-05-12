"""
Compare metrics to evaluate text simplification results
"""
import pandas as pd
from eval_utils.text_simplification_evaluation import *


def build_metrics_table(list_of_value_lists, models, metric_names):
    """
    list_of_value_lists: list of lists
    Each inner list = one model's values
    """
    n_rows = len(list_of_value_lists[0])

    df = pd.DataFrame({
        "metric": metric_names
    })

    for i, values in enumerate(list_of_value_lists):
        df[models[i]] = values

    return df


def save_with_coloring(df, output_file):
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")

        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        # Apply formatting to ALL model columns
        for col_idx in range(1, df.shape[1]):  # skip "metric"
            col_letter = chr(ord('A') + col_idx)
            cell_range = f"{col_letter}2:{col_letter}{len(df) + 1}"

            values = df.iloc[:, 1:].to_numpy().flatten()

            worksheet.conditional_format(cell_range, {
                "type": "3_color_scale",
                "min_type": "num",
                "mid_type": "num",
                "max_type": "num",
                "min_value": values.min(),
                "mid_value": 0,
                "max_value": values.max(),
                "min_color": "#8B0000",  # dark red
                "mid_color": "#FFFFFF",
                "max_color": "#006400",  # dark green
            })


icd_code = "6A20"
lang = "fr"
# type_of_metrics = 'similarity'
type_of_metrics = 'tokens_types'
# type_of_metrics = 'complexity'

metric_names = ['diff_tokens', 'diff_types']
# metric_names = ['bleu', 'rouge1', 'rougeL', 'bertscore']
# metric_names = ['diff_ttr', 'diff_mattr', 'diff_mtld',
#                 'diff_lix', 'diff_rix',
#                 'diff_flesch_reading_ease', 'diff_flesch_kincaid_grade',
#                 'diff_smog_index', 'diff_gunning_fog',
#                 'diff_coleman_liau_index', 'diff_automated_readability_index',
#                 'diff_dale_chall_readability_score']

# metric_names = ['diff_ttr', 'diff_mattr', 'diff_mtld',
#                 'diff_lix', 'diff_rix',
#                 'diff_flesch_reading_ease']

# models = ['lingconv', 'prism', 'ascle', 'biomistral']
models = ['biomistral']

all_results = []
all_models = []

for model in models:
    filepath = f"../results/{lang}/{icd_code}/{model}_model_results.tsv"
    data = read_tsv_3cols(filepath)

    for line in data[1:]:
        all_models.append(line[0])
        original = line[1]
        simplified = line[2]

        # bleu, rouge, bertscore
        bleu = float(get_bleu(original, simplified)['bleu'])

        rouge = get_rouge(original, simplified)
        rouge1 = rouge['rouge1']['f1']
        rougel = rouge['rougeL']['f1']

        bertscore = get_bert_score(original, simplified)

        # drop in complexity metrics
        complexity_original = get_lexical_richness(original)
        complexity_simplified = get_lexical_richness(simplified)

        diff_tokens = complexity_original['words'] - complexity_simplified['words']
        diff_types = complexity_original['unique_words'] - complexity_simplified['unique_words']

        diff_ttr = complexity_original['ttr'] - complexity_simplified['ttr']
        diff_mattr = complexity_original['mattr'] - complexity_simplified['mattr']
        diff_mtld = complexity_original['mtld'] - complexity_simplified['mtld']

        # drop in readability
        diff_lix = get_lix_score(original) - get_lix_score(simplified)
        diff_rix = get_rix_score(original) - get_rix_score(simplified)

        orig_readability = get_readability_metrics(original, lang)
        simpl_readability = get_readability_metrics(simplified, lang)

        diff_flesch_reading_ease = orig_readability['flesch_reading_ease'] - simpl_readability['flesch_reading_ease']

        # for English only
        diff_flesch_kincaid_grade = orig_readability['flesch_kincaid_grade'] - simpl_readability['flesch_kincaid_grade']
        diff_smog_index = orig_readability['smog_index'] - simpl_readability['smog_index']
        diff_gunning_fog = orig_readability['gunning_fog'] - simpl_readability['gunning_fog']
        diff_coleman_liau_index = orig_readability['coleman_liau_index'] - simpl_readability['coleman_liau_index']
        diff_automated_readability_index = orig_readability['automated_readability_index'] - simpl_readability[
            'automated_readability_index']
        diff_dale_chall_readability_score = orig_readability['dale_chall_readability_score'] - simpl_readability[
            'dale_chall_readability_score']

        # values = [diff_ttr, diff_mattr, diff_mtld, diff_lix, diff_rix,
        #           diff_flesch_reading_ease, diff_flesch_kincaid_grade,
        #           diff_smog_index, diff_gunning_fog,
        #           diff_coleman_liau_index, diff_automated_readability_index,
        #           diff_dale_chall_readability_score]

        # values = [diff_ttr, diff_mattr, diff_mtld, diff_lix, diff_rix,
        #           diff_flesch_reading_ease]

        # values = [bleu, rouge1, rougel, bertscore]

        values = [diff_tokens, diff_types]

        all_results.append(values)


df = build_metrics_table(all_results, all_models, metric_names)
save_with_coloring(df, f"../results/{lang}/{icd_code}/colored_metrics_{type_of_metrics}.xlsx")
