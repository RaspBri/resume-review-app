import os
from PyPDF2 import PdfReader
from pathlib import Path

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
UPLOAD_FOLDER = os.path.join(base_dir, 'resources')

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    # print((reader.pages[0].extract_text()))
    for page in reader.pages:
        text = page.extract_text()
        print(text + '\n*** END OF PAGE ***\n')
    
    
if __name__ == '__main__':
    pdf_path = Path(UPLOAD_FOLDER)
    extract_text_from_pdf(str(pdf_path))