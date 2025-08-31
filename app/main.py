import os, requests, logging, spacy, re, string
import pandas as pd
from PyPDF2 import PdfReader
from pathlib import Path
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from google import genai
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
UPLOAD_FOLDER = os.path.join(base_dir, 'resources')
    
load_dotenv()
nlp = spacy.load("en_core_web_lg") 
model = SentenceTransformer('all-MiniLM-L6-v2')

BLACKLIST = {
    "experience", "understanding", "record", "tools", "field", "degree",
    "track", "team", "teams", "hands", "ability", "background", "mindset",
    "development", "quality", "skills", "platforms", "languages", "code",
    "science", "engineering", "proficiency", "expertise", "knowledge",
    "bachelor", "software", "frameworks", "design", "issues", "patients",
    "preferred years", "years", "communication", "leadership", "problem",
    "management", "methodologies", "other", "the", "they", "proper", "rate",
    "learning", 
}

def get_similarity(text1, text2):
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2)[0][0])

def is_valid_keyword(keyword):
    keyword = keyword.lower().strip()
    keyword = keyword.translate(str.maketrans('', '', string.punctuation))  # remove punctuation

    if keyword in BLACKLIST:
        return False

    for word in keyword.split():
        if word in BLACKLIST:
            return False

    return True

def get_job_info():
    job_title = input("Enter Job Title: ")
    job_description = input("Enter Job Description: ")
    job_skills = input("Enter Job Responsibilities and Required Skills: ")

    # Remove non alpahbet chars
    job_title_words = re.findall(r'\b[a-zA-Z]+\b', job_title)
    job_description_words = re.findall(r'\b[a-zA-Z]+\b', job_description)
    job_skills_words = re.findall(r'[a-zA-Z0-9+/.-]+(?:\s+[a-zA-Z0-9+/.-]+)*', job_skills)

    cleaned_job_title = ' '.join(job_title_words)
    cleaned_job_description = ' '.join(job_description_words)
    cleaned_job_skills = ' '.join(job_skills_words)
    
    return cleaned_job_title , (cleaned_job_description + ' ' + cleaned_job_skills)

def extract_text_from_pdf(pdf_file):
    pdf_text = ''
    try:
        with open(pdf_file, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pdf_text += text + '\n'
    except Exception as e:
        print(f"Error: {e}")
        return '' 
    
    # remove non alpha chars
    words = re.findall(r'\b[a-zA-Z]+\b', pdf_text)
    cleaned_text = ' '.join(words)

    return cleaned_text

def calculate_applicant_resume_match(resume_text, job_keywords):
    resume_text = resume_text.lower()
    matches = [kw for kw in job_keywords if kw in resume_text]
    unmatched = [kw for kw in job_keywords if kw not in resume_text]
    if not job_keywords:
        return 0.0
    match_score = round(len(matches) / len(job_keywords), 2)

    return match_score, unmatched

def extract_keywords(text):
    doc = nlp(text)
    keywords = set()

    filtered_keywords = [
        token.text.lower()
        for token in doc
        if token.pos_ in {"NOUN", "PROPN"} and token.text.lower() not in nlp.Defaults.stop_words and token.is_alpha
    ]

    for kw in filtered_keywords:
        if is_valid_keyword(kw):
            keywords.add(kw)

    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        if 1 < len(phrase) < 50 and is_valid_keyword(phrase):
            keywords.add(phrase)

    split_keywords = set()
    for kw in keywords:
        parts = re.split(r'[,/]| and |\s+', kw)
        parts = [p.strip() for p in parts if p.strip() != '']
        for part in parts:
            if is_valid_keyword(part):
                split_keywords.add(part)

    return split_keywords

def get_contextual_info(text):
    doc = nlp(text)
    nouns = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 1]
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    entities = [ent.text for ent in doc.ents]

    return {
        "nouns": nouns,
        "verbs": verbs, 
        "entities": entities, 
        "full_doc": doc
    }

def applicant_advice(keyword_score, unmatched_kw, job_title, similarity_score):
    ai_response = 'Some words from Gemini: \n\n'
    similarity_score_note = 'Passing Similarity Score'

    if keyword_score <= 70:
        print('Keyword match score is below 70%. You might have forgot to add the following skills.')
        print(','.join(unmatched_kw))

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents = f"I want a job with this title {job_title} but need help with the following skills {unmatched_kw}. Suggest free resources I can use to upskill, and 1 paid option."
        )
        print(response.text)
        ai_response = response.text
        
    if similarity_score <= 50:
        similarity_score_note = 'Low applicant to job similarity score.'
        
    return ai_response, similarity_score_note

def process_resume_and_job(file_pdf, job_description, job_title):
    print(file_pdf)
    print(job_description)
    pdf_path = Path(UPLOAD_FOLDER)
    resume_pdf = (os.listdir(pdf_path))[1]
    resume_text = extract_text_from_pdf(str(UPLOAD_FOLDER + '/' + resume_pdf))
    # job_title, job_description_and_skills = get_job_info()
    job_description_and_skills = job_description

    job_skills_keywords = extract_keywords(job_description_and_skills)
    keyword_score, unmatched_words = calculate_applicant_resume_match(resume_text, job_skills_keywords)
    print('Applicant Keyword Match: % ' + str(keyword_score * 100))

    similarity_score = (get_similarity(resume_text, job_description_and_skills)) * 100
    print('Applicant Resume To Job Match Score: % ' + str(similarity_score))

    # ai_response, similarity_score_note = applicant_advice(keyword_score, unmatched_words, job_title, similarity_score)

    return {
        'keyword_match': str(keyword_score * 100),
        'resume_to_job_similarity': similarity_score,
        'similarity_score_note': "similarity_score_note",
        'missing_keywords': unmatched_words,
        'upskilling_advice': "ai_response"
    }

    