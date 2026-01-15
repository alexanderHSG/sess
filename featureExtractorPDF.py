from pptx import Presentation
import statistics
import os
import csv
import pandas as pd
import math
import pdfplumber
from concurrent.futures import ThreadPoolExecutor, as_completed

def analyze_slidedeck_pdf(pdf_path):
    word_counts = []
    numImages = []
    numPages = 0


    try:
        with pdfplumber.open(pdf_path) as pdf:
            numPages = len(pdf.pages)
            all_text = ''
            for page in pdf.pages:
                text = page.extract_text()
                images = page.images
                numImagesPage = len(images)
                #add of images into array
                numImages.append(numImagesPage)
                if text:
                    words = text.split()
                    word_count = len(words)
                    word_counts.append(word_count)
                all_text = all_text + text
    except Exception as e:
        print(f"Error with file: {pdf_path}. Error: {e}")
        return None

    if len(word_counts) == 0:
        word_counts = [1]

    if len(numImages) == 0:
        numImages = [1]

    mean_numImages = statistics.mean(numImages)
    std_numImages = statistics.stdev(numImages) if len(numImages) > 1 else 0
    total_numImages = sum(numImages)    

    mean_numWords = statistics.mean(word_counts)
    std_numWords = statistics.stdev(word_counts) if len(word_counts) > 1 else 0
    total_numWords = sum(word_counts)

    for i in range(0, len(word_counts)):
        if word_counts[i] == 0 or word_counts[i] == 1:
            word_counts[i] = 2

    enumPages = numPages if numPages > 1 else 2

    entropy = 0
    for i in range(0, len(word_counts)):
        entropy += word_counts[i] * math.log(word_counts[i])
    entropy = -entropy
    entropy = entropy / math.log(enumPages)
    entropy = entropy / math.log(max(word_counts))
    entropy = 1 - entropy

    readability = 1 - sum(word_counts) / enumPages
    content = None

    if all_text:
        content = all_text

    return {
        'total_numImages': total_numImages,
        'std_numImages': std_numImages,
        'mean_numWords': mean_numWords,
        'std_numWords': std_numWords,
        'total_numWords': total_numWords,
        'entropy': entropy,
        'numPages': numPages,
        'readability': readability,
        'content': content
    }

def analyze_pdf_presentations(folder):
    folder = os.path.join(os.path.dirname(os.path.abspath("__file__")), folder)
    pdf_path = os.path.join(folder, file['id'] + '.pdf')
    speakerdeck = pd.read_csv('speakerdeck.csv')


    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(analyze_single_pdf, pdf_path): file for index, file in speakerdeck.iterrows()}
        for future in as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                if result is not None:
                    index = speakerdeck[speakerdeck['id'] == file['id']].index[0]
                    for key, value in result.items():
                        speakerdeck.at[index, key] = value
            except Exception as e:
                print(f"Error processing file: {file['id']}. Error: {e}")

    return speakerdeck


if __name__ == "__main__":
    folder = "presentationsspeakerdeckpdf"
    result = analyze_pdf_presentations(folder)
    result.to_csv('speakerdeckfeatures1.csv', index=False)
