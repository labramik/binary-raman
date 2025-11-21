#!/usr/bin/env python3
"""
Extract band positions and temperatures from annotated Raman spectroscopy figures.

This script uses OCR (via pytesseract/easyocr) to extract text annotations from 
Raman spectrum figures showing temperature-dependent data.

Usage:
    python extract_annotations.py <image_path>

Requirements:
    pip install pillow pytesseract easyocr opencv-python numpy --break-system-packages
"""

import sys
import re
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("Warning: PIL or pytesseract not available. Install with: pip install pillow pytesseract --break-system-packages")
    pytesseract = None

try:
    import easyocr
    import cv2
    import numpy as np
except ImportError:
    print("Warning: easyocr not available. Install with: pip install easyocr opencv-python --break-system-packages")
    easyocr = None


def extract_with_pytesseract(image_path):
    """Extract text using pytesseract."""
    if pytesseract is None:
        return None
    
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


def extract_with_easyocr(image_path):
    """Extract text using easyocr."""
    if easyocr is None:
        return None
    
    reader = easyocr.Reader(['en'])
    result = reader.readtext(str(image_path))
    
    # Extract text and positions
    extracted = []
    for (bbox, text, confidence) in result:
        extracted.append({
            'text': text,
            'confidence': confidence,
            'position': bbox
        })
    
    return extracted


def parse_bands(text):
    """Extract Raman band positions (wavenumbers) from text."""
    # Match numbers that could be wavenumbers (typically 50-4000 cm⁻¹)
    band_pattern = r'\b([5-9]\d|[1-9]\d{2,3})\b'
    bands = re.findall(band_pattern, text)
    return [int(b) for b in bands if 50 <= int(b) <= 4000]


def parse_temperatures(text):
    """Extract temperatures in Kelvin from text."""
    # Match patterns like "254.15 K", "RT", "room temperature"
    temp_pattern = r'(\d{2,3}(?:\.\d{1,2})?)\s*K'
    temps = re.findall(temp_pattern, text)
    
    temperatures = [float(t) for t in temps]
    
    # Check for RT (room temperature)
    if re.search(r'\bRT\b|room\s+temp', text, re.IGNORECASE):
        temperatures.append('RT')
    
    return temperatures


def main(image_path):
    """Main extraction function."""
    print(f"Analyzing image: {image_path}\n")
    
    # Try pytesseract first
    print("Attempting extraction with pytesseract...")
    text_simple = extract_with_pytesseract(image_path)
    
    if text_simple:
        print("Extracted text:")
        print(text_simple)
        print("\n" + "="*50 + "\n")
        
        bands = parse_bands(text_simple)
        temps = parse_temperatures(text_simple)
        
        print(f"Detected band positions: {bands}")
        print(f"Detected temperatures: {temps}")
    else:
        print("pytesseract not available or failed.")
    
    # Try easyocr for better results
    print("\nAttempting extraction with easyocr...")
    ocr_results = extract_with_easyocr(image_path)
    
    if ocr_results:
        print(f"\nFound {len(ocr_results)} text elements:")
        for item in ocr_results:
            print(f"  '{item['text']}' (confidence: {item['confidence']:.2f})")
        
        # Combine all text
        combined_text = ' '.join([item['text'] for item in ocr_results])
        bands = parse_bands(combined_text)
        temps = parse_temperatures(combined_text)
        
        print(f"\nDetected band positions: {bands}")
        print(f"Detected temperatures: {temps}")
    else:
        print("easyocr not available or failed.")
    
    print("\n" + "="*50)
    print("Note: Manual verification recommended.")
    print("Check the figure visually to confirm all annotations were captured.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_annotations.py <image_path>")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    main(image_path)
