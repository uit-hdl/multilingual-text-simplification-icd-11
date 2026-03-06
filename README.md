Text simplification / paraphrasing of ICD-11 texts for creating a parallel multilingual knowledge base on mental health

### Pipeline:

1) ```src/extract_icd_texts.py```: browses through 
ICD API, finds the latest release of ICD-11 
linearizations, extracts the definitions for 
the chosen ICD code (e.g. 6A20 for Schizophrenia) 
and for the chosen list of languages (here: English, 
French, Czech, Turkish, German pre-released), 
stores the results in a TSV file 
in ```results/parallel_icd_texts_{icd_code}.tsv```

**Note**: For running this code, one needs to get ICD
 API access [here](https://icd.who.int/icdapi)

2) ```src/extract_dutch_icd_texts.py```: opens the page
 of the ICD related files by *"WHO Collaborating 
 Centre for the Family of International Classifications
  (FIC) in the Netherlands"*, finds the latest release
   of the available XML file of ICD-10, downloads it, 
   parses and finds a definition for the given 
   code (F20 for Schizophrenia), and appends the 
   extracted results to the 
   results file
    ```results/parallel_icd_texts_{icd_code}.tsv```.
    The link to the found ZIP file is stored in 
    ```data/dutch/dutch_icd10```