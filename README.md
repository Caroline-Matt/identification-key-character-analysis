# Morphological Character Frequency Analysis of the Identification Keys in *Key to the Vascular Plants of Inner Mongolia*

**Author:** Wen-Xuan Yue
**ORCID:** https://orcid.org/0009-0001-1298-6626
**Affiliation:** School of Life Sciences, Lanzhou University
**Date:** 2026-06-11

---

## 1. Project Overview

This project quantitatively analyzes the morphological characters used in the angiosperm family-level identification keys of *Key to the Vascular Plants of Inner Mongolia*.

The objectives of this study are:

1. To quantify the frequency of different organ characters used in the identification keys;
2. To quantify the frequency of different floral character categories;
3. To evaluate differences among character categories;
4. To explore the morphological characters most frequently employed in plant taxonomic identification.

The statistical unit of analysis is the **key entry** (e.g., "1a.", "1b.", "2a.", "2b."), rather than the number of keyword occurrences in the entire text.

---

## 2. File Description

### Key to the Vascular Plants of Inner Mongolia.pdf

Original reference document.

**Not included in this repository due to copyright restrictions. Please obtain a copy independently.**

### pdfToTxt.py

OCR extraction script.

### pdfToTxt_output.txt

OCR-generated text file.

### KeyFeatureAnalysis.py

Main data analysis script.

### 检索表关键词统计.xlsx

Statistical results and analysis outputs.

### plot_ci.py

Visualization script.

### 器官置信区间图.png

Frequency and confidence interval plot of organ characters.

### 花特征置信区间图.png

Frequency and confidence interval plot of floral character categories.

### README.txt

Project documentation.

---

## 3. Data Processing Workflow

### 1. OCR Extraction

The original PDF was converted into machine-readable text using PaddleOCR.

### 2. Key Entry Segmentation

Based on the structure of botanical identification keys, entries beginning with labels such as "1a.", "1b.", "2a.", and "2b." were recognized as independent key entries.

### 3. Character Identification

Character categories were identified using predefined keyword dictionaries.

#### Organ Character Categories

* Flower
* Leaf
* Stem
* Root
* Fruit
* Seed

#### Floral Character Categories

* Inflorescence
* Perianth
* Stamens
* Pistils
* Floral sexuality
* Ovary position
* Connation and separation
* Floral symmetry
* Bract structure
* Specialized floral structures

Within a single key entry, each category was counted at most once.

### 4. Statistical Analysis

Character frequencies were calculated across all key entries.

Bootstrap resampling (1,000 iterations) was used to estimate 95% confidence intervals (95% CI).

Differences between character categories were evaluated by examining whether the 95% confidence interval of the bootstrap difference distribution included zero.

---

## 4. Interpretation of Results

### Organ Character Frequency Plot

* **Point:** observed frequency
* **Horizontal bar:** Bootstrap 95% confidence interval
* **Letter grouping:** significance grouping

Interpretation of letter grouping:

* Categories sharing the same letter indicate no obvious difference.
* Categories assigned different letters indicate a relatively clear difference.

The floral character frequency plot is interpreted in the same manner.

---

## 5. Software Environment

Python 3.11

### Main Dependencies

* pandas
* numpy
* openpyxl
* matplotlib
* scipy

---

## 6. AI Usage Statement

Large language models (ChatGPT) were used to assist with code development, debugging, workflow design, and language refinement.

AI tools were not involved in data collection, statistical result generation, interpretation of results, or formulation of conclusions.

All code, parameter settings, statistical analyses, and conclusions were reviewed and validated by the author, who assumes full responsibility for the content.

---

## 7. Data Availability

The OCR-generated text data, keyword dictionaries, Python source code, and statistical outputs are included in this project repository.

Researchers may use these materials to reproduce the complete data processing and statistical analysis workflow described in this study.

---

## 8. License

This project is licensed under the MIT License.