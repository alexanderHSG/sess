"""PDF slide deck feature extraction."""

from __future__ import annotations

import math
import statistics
from typing import Any

import pdfplumber


def analyze_slidedeck_pdf(pdf_path: str) -> dict[str, Any] | None:
    word_counts: list[int] = []
    image_counts: list[int] = []
    num_pages = 0
    all_text_parts: list[str] = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                image_counts.append(len(page.images))

                if text:
                    words = text.split()
                    word_counts.append(len(words))
                    all_text_parts.append(text)
    except Exception:
        return None

    if not word_counts:
        word_counts = [1]

    if not image_counts:
        image_counts = [1]

    std_num_images = statistics.stdev(image_counts) if len(image_counts) > 1 else 0
    total_num_images = sum(image_counts)

    mean_num_words = statistics.mean(word_counts)
    std_num_words = statistics.stdev(word_counts) if len(word_counts) > 1 else 0
    total_num_words = sum(word_counts)

    adjusted_word_counts = [max(value, 2) for value in word_counts]
    enum_pages = num_pages if num_pages > 1 else 2

    entropy = 0.0
    for value in adjusted_word_counts:
        entropy += value * math.log(value)
    entropy = -entropy
    entropy = entropy / math.log(enum_pages)
    entropy = entropy / math.log(max(adjusted_word_counts))
    entropy = 1 - entropy

    readability = 1 - sum(adjusted_word_counts) / enum_pages
    content = " ".join(all_text_parts) if all_text_parts else None

    return {
        "total_numImages": total_num_images,
        "std_numImages": std_num_images,
        "mean_numWords": mean_num_words,
        "std_numWords": std_num_words,
        "total_numWords": total_num_words,
        "entropy": entropy,
        "numPages": num_pages,
        "readability": readability,
        "content": content,
    }
