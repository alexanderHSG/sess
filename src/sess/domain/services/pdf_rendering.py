"""PDF rendering helpers."""

from __future__ import annotations

import io
import time

import fitz
from PIL import Image


def process_pdf_to_images(pdf_path: str) -> list[Image.Image]:
    images: list[Image.Image] = []
    with fitz.open(pdf_path) as document:
        for page_num in range(len(document)):
            time.sleep(0.1)
            page = document.load_page(page_num)
            pixmap = page.get_pixmap()
            image = Image.open(io.BytesIO(pixmap.tobytes("ppm")))
            images.append(image)
    return images

