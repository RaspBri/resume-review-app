import os
from PyPDF2 import PdfReader
from pathlib import Path

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    # print((reader.pages[0].extract_text()))
    for page in reader.pages:
        text = page.extract_text()
        print(text + '\n*** END OF PAGE ***\n')
    
if __name__ == '__main__':
    pdf_path = Path("/Users/brimurray/Desktop/VSCode/resume-review-app/resources/resume1.pdf")
    extract_text_from_pdf(str(pdf_path))