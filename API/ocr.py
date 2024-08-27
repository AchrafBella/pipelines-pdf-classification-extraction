from pdfminer.high_level import extract_text

def pdf_to_text(pdf_path):
    text = extract_text(pdf_path)
    return text
