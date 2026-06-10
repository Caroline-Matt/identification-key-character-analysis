"""
Script Name: pdfToTxt.py

Author: Wen-Xuan Yue
ORCID: https://orcid.org/0009-0001-1298-6626
Affiliation: School of Life Sciences, Lanzhou University
Date: 2026-06-10

## Description

This script converts scanned pages from the angiosperm family-level
identification keys in *Key to the Vascular Plants of Inner Mongolia*
into machine-readable text for subsequent quantitative analysis of
morphological characters.

## Input

Key to the Vascular Plants of Inner Mongolia.pdf

## Output

pdfToTxt_output.txt

## Workflow

1. Render PDF pages as images using PyMuPDF.
2. Perform optical character recognition (OCR) using PaddleOCR.
3. Export recognized text to a UTF-8 encoded TXT file.

## Parameters

START_PAGE : int
Starting page number (default: 35)

END_PAGE : int
Ending page number (default: 368)

ZOOM : float
Rendering scale factor for OCR (default: 2.5)

## Software Environment

Python 3.11

## Required Packages

paddlepaddle==2.6.2
paddleocr==2.7.3
pymupdf
tqdm

## Notes

This script was developed for extracting text from the angiosperm
identification keys of *Key to the Vascular Plants of Inner Mongolia*.

The OCR output serves as the input for subsequent analyses,
including key-entry segmentation, character identification,
frequency estimation, bootstrap analysis, and visualization.

Because OCR errors may occur, manual inspection and data cleaning
are recommended before performing statistical analyses.

"""

from pathlib import Path
import os

os.environ["FLAGS_use_mkldnn"] = "0"

import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from tqdm import tqdm


PDF_PATH = Path(__file__).parent / "内蒙古维管植物检索表.pdf"     # PDF文件位置
OUTPUT_TXT = Path(__file__).parent / "pdfToTxt_output.txt"      #输出文件位置

START_PAGE = 35     #分科检索表开始页码
END_PAGE = 368      #分科检索表结束页码
ZOOM = 2.5          # PDF渲染倍率


def render_page_to_image(pdf_doc, page_index, image_path, zoom=2.5):
    page = pdf_doc[page_index]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    pix.save(str(image_path))


def ocr_image(ocr, image_path):
    result = ocr.ocr(str(image_path), cls=True)

    lines = []

    if not result or not result[0]:
        return ""

    for item in result[0]:
        text = item[1][0]
        lines.append(text)

    return "\n".join(lines)


def main():
    temp_dir = Path(__file__).parent / "_temp_pages"
    temp_dir.mkdir(exist_ok=True)

    ocr = PaddleOCR(
    use_angle_cls=True,
    lang="ch",
    show_log=False,
    enable_mkldnn=False
    )

    doc = fitz.open(PDF_PATH)
    total_pages = len(doc)

    start_index = START_PAGE - 1
    end_index = total_pages if END_PAGE is None else END_PAGE

    all_text = []

    for page_index in tqdm(range(start_index, end_index), desc="OCR"):
        page_no = page_index + 1
        image_path = temp_dir / f"page_{page_no:04d}.png"

        render_page_to_image(doc, page_index, image_path, zoom=ZOOM)

        page_text = ocr_image(ocr, image_path)
        image_path.unlink()

        all_text.append(f"\n\n===== Page {page_no} =====\n\n{page_text}")

    OUTPUT_TXT.write_text("\n".join(all_text), encoding="utf-8")

    print("完成")
    print(f"TXT 输出：{OUTPUT_TXT}")


if __name__ == "__main__":
    main()
