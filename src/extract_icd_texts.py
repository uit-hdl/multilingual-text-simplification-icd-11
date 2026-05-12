"""
A pipeline extracting texts in different languages from ICD-11
and making a parallel TSV corpus
"""

import logging
import requests
import pandas as pd
import os

TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


# get texts in for a specific disease code
def find_texts_by_icd_code(headers, latest_release_url, icd_code):
    # list of tuples (code, text)
    results = []

    url = f"{latest_release_url}"

    # also show text with diagnostic criteria
    params = {
        "include": "diagnosticCriteria"
    }

    # browse mental disorders
    r = requests.get(url, headers=headers).json()
    for child in r['child']:
        disease_class = requests.get(child, headers=headers).json()

        # code 06 for "Mental, behavioural or neurodevelopmental disorders"
        if disease_class['code'] == '06':

            # browse subclass; it doesn't have a code, so we continue browsing the children links of all subclasses
            for disease_class_child in disease_class['child']:
                disease_subclass = requests.get(disease_class_child, headers=headers).json()

                # browse diseases
                if disease_subclass.get('child'):
                    for disease_subclass_child in disease_subclass['child']:
                        disease = requests.get(disease_subclass_child, headers=headers, params=params).json()

                        # locate schizophrenia by its code
                        if disease['code'] == icd_code:

                            # add to results
                            if disease.get('definition'):
                                results.append((icd_code, disease['definition']['@value']))

                            # if there are diagnostic criteria,
                            # also add a row with the same code + '_criteria'
                            # if disease.get('diagnosticCriteria'):
                            #     results.append((icd_code + '_criteria', disease['diagnosticCriteria']['@value']))

                            # check if there are additional subpages to this definition
                            if disease.get('child'):
                                for found_disease_child in disease['child']:
                                    sub_disease_page = requests.get(found_disease_child, headers=headers).json()

                                    # add to results the definitions of subpages
                                    if sub_disease_page.get('definition'):
                                        results.append((sub_disease_page['code'],
                                                        sub_disease_page['definition']['@value']))

    return results


# access ICD API and get a definition in a chosen language
# available TRUSTING languages: en, fr, cs, tr, de
# to access ICD API: register at https://icd.who.int/icdapi
def get_icd_text(lang="en", icd_code="6A20"):
    token_resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "icdapi_access",
            "grant_type": "client_credentials",
        },
    )

    token = token_resp.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": lang,
        "API-Version": 'v2'
    }

    icd_entity_url = "https://id.who.int/icd/entity"

    # open the initial entity page first
    r = requests.get(icd_entity_url, headers=headers)
    icd_entity_data = r.json()

    # find the latest release of the ICD definitions
    latest_release_url = icd_entity_data['includedLinearizations'][0]

    # browse ICD and find the definition by the disease's code
    results = find_texts_by_icd_code(headers, latest_release_url, icd_code)
    return latest_release_url, results


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    # list of needed languages:
    # English, French, German
    languages = ['en', 'fr', 'de']

    # 6A20: code for Schizophrenia
    # 6A20-6A25: primary psychotic disorders
    icd_code = "6A20"

    # rows to write to a dataframe
    rows = []

    # open a csv file
    parent = os.path.dirname(os.getcwd())
    folderpath = os.path.join(parent, f"results/{icd_code}")
    if not os.path.exists(folderpath):
        os.mkdir(folderpath)

    results_path = os.path.join(folderpath, f"parallel_icd_texts_{icd_code}.tsv")

    for language in languages:
        logger.info(f"Loading texts in language: {language}")
        release_url, results = get_icd_text(language, icd_code)

        for result in results:
            logger.info("Writing a row of results")
            rows.append({"release_url": release_url,
                         "language": language,
                         "code": result[0],
                         "original_text": result[1]})

    df = pd.DataFrame(rows)
    df.to_csv(results_path, mode='a', sep='\t', index=False)


if __name__ == '__main__':
    main()
