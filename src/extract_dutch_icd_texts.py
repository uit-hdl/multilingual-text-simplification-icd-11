"""
Extract ICD-10 texts in Dutch
available at https://class.whofic.nl/
"""

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree
import zipfile
import logging
import requests
import os
import re


# find a link to the latest release of ICD-10
def find_icd_10_link():
    url = "https://www.whofic.nl/downloads-en-links/icd-10-bestanden-voor-gebruik-in-lmrlbz"
    r = requests.get(url)

    # parse HTML
    soup = BeautifulSoup(r.text, "html.parser")

    # get table with links to files
    table = soup.find("table")

    # latest version of ICD-10 is in the first row (after the header)
    latest_version = table.find_all("tr")[1]

    # find the latest link to the document page
    cols = latest_version.find_all("td")
    link = cols[0].find("a")["href"]

    # get the link to *.zip file from that page
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")

    zip_link = None

    for link in soup.find_all("a", href=True):
        if link["href"].endswith(".zip"):
            zip_link = link["href"]

    return zip_link


# download the latest release of ICD-10 in *.xml format
def download_icd_10_file(url):
    filepath = '../data/dutch/dutch_icd10'

    # save file
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(f"{filepath}.zip", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # unzip
    with zipfile.ZipFile(f"{filepath}.zip", "r") as z:
        z.extractall(filepath)

    # remove also the zip file
    os.remove(f"{filepath}.zip")


# parse XML tree and find the definition for the given ICD code
def parse_xml_icd10(filepath, icd_code):
    result = ''

    tree = ElementTree.parse(filepath)
    root = tree.getroot()

    # find all <Class> elements recursively
    for class_tag in root.findall(".//Class"):
        code = class_tag.get("code")
        found_class = class_tag

        # get the definition when found the needed ICD code
        if code == icd_code:
            for rubric in found_class.findall(".//Rubric"):
                kind = rubric.get("kind")
                if kind == "description":
                    text = ElementTree.tostring(rubric, encoding="unicode")

                    # remove all tags and extra spaces
                    without_tags = re.sub(r"<[^>]+>", "", text)
                    clean_text = "\n".join(line.strip() for line in without_tags.splitlines() if line.strip())
                    result += clean_text + ' '

    return result


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    dutch_folder = "../data/dutch/dutch_icd10"

    # F20: code for Schizophrenia in ICD-10 we don't get sub codes,
    # because they significantly differ in content from ICD-11 (different types of schizophrenia described)
    # description of F20 in ICD-10 is relatively similar to 6A20 in ICD-11
    icd_code_10 = "F20"

    # check if .xml file already exists
    xml_exists = any(
        f.lower().endswith(".xml") and os.path.isfile(os.path.join(dutch_folder, f))
        for f in os.listdir(dutch_folder)
    )

    if not xml_exists:
        logger.info(f"Finding a link to the latest Dutch ICD-10")
        icd10_url = find_icd_10_link()

        # just to write it down once and use it later when parsing XML and writing results into the TSV file
        with open(f'{dutch_folder}/release_url_link.txt', 'w') as f:
            f.write(icd10_url)

        logger.info(f"Found a link: {icd10_url}")
        logger.info(f"Downloading the ZIP file")
        download_icd_10_file(icd10_url)

        logger.info(f"XML ICD-10 file is ready")

    # find XML file
    dutch_icd10_filepath = ''
    for filename in os.listdir(dutch_folder):
        if filename.endswith('xml'):
            dutch_icd10_filepath = os.path.join(dutch_folder, filename)
            break

    logger.info(f"Extracting description for the code {icd_code_10}")
    result_text = parse_xml_icd10(dutch_icd10_filepath, icd_code_10)

    # we assume that ICD-11 has been extracted first and the file exists
    # replace F (ICD-10) to 6A (ICD-11)
    icd_code_11 = icd_code_10.replace('F', '6A')
    results_path = f"../results/parallel_icd_texts_{icd_code_11}.tsv"

    # get link for the latest release
    with open(f'{dutch_folder}/release_url_link.txt', 'r') as f:
        icd10_url = f.read()

    # nl code stands for dutch
    logger.info(f"Writing extracted text to results file: {results_path}")
    with open(results_path, 'a') as f:
        f.write(f"{icd10_url}\tnl\t{icd_code_10}\t{result_text}\n")


if __name__ == '__main__':
    main()
