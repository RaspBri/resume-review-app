import os, requests, logging, spacy, re, string
import pandas as pd
from PyPDF2 import PdfReader
from pathlib import Path
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from google import genai
from dotenv import load_dotenv
from transformers import AutoTokenizer, pipeline, AutoModelForTokenClassification

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
UPLOAD_FOLDER = os.path.join(base_dir, 'resources')
    
load_dotenv()
nlp = spacy.load("en_core_web_lg") 
model = SentenceTransformer('all-MiniLM-L6-v2')

token_skill_classifier = pipeline(model="jjzha/jobbert_skill_extraction", aggregation_strategy="first")
token_knowledge_classifier = pipeline(model="jjzha/jobbert_knowledge_extraction", aggregation_strategy="first")

# skill_tokenizer = AutoTokenizer.from_pretrained("jjzha/jobbert_skill_extraction")
# skill_model = AutoModelForTokenClassification.from_pretrained("jjzha/jobbert_skill_extraction")
# token_skill_classifier = pipeline("token-classification", model=skill_model, tokenizer=skill_tokenizer, aggregation_strategy="first", max_length=512)

# knowledge_tokenizer = AutoTokenizer.from_pretrained("jjzha/jobbert_knowledge_extraction")
# knowledge_model = AutoModelForTokenClassification.from_pretrained("jjzha/jobbert_knowledge_extraction")
# token_knowledge_classifier = pipeline("token-classification", model=knowledge_model, tokenizer=knowledge_tokenizer, aggregation_strategy="first", max_length=512)

BLACKLIST = {
    "experience", "understanding", "record", "tools", "field", "degree",
    "track", "team", "teams", "hands", "ability", "background", "mindset",
    "development", "quality", "skills", "platforms", "languages", "code",
    "science", "engineering", "proficiency", "expertise", "knowledge",
    "bachelor", "software", "frameworks", "design", "issues", "patients",
    "preferred years", "years", "communication", "leadership", "problem",
    "management", "methodologies", "other", "the", "they", "proper", "rate",
    "learning", "attention to detail"
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
        return 0, [], []
    
    match_score = round(len(matches) / len(job_keywords), 2)

    return match_score, unmatched, matches

def aggregate_span(results):
    new_results = []
    current_result = results[0]

    for result in results[1:]:
        if result['start'] == current_result['end'] + 1:
            current_result['word'] += ' ' + result['word']
            current_result['end'] = result['end']
        else:
            new_results.append(current_result)
            current_result = result
    
    new_results.append(current_result)

    return new_results

def extract_keywords(text):

    output_skills = token_skill_classifier(text)
    for result in output_skills:
        if result.get('entity_group'):
            result['entity'] = 'Skill'
            del result['entity_group']
    
    output_knowledge = token_knowledge_classifier(text)
    for result in output_knowledge:
        if result in output_skills:
            if result.get('entity_group'):
                result['entity'] = 'Knowledge'
                del result['entity_group']

    if len(output_skills) > 0:
        output_skills = aggregate_span(output_skills)
    if len(output_knowledge) > 0:
        output_knowledge = aggregate_span(output_knowledge)
    
    return {'text': text, 'entities': output_skills}, {'text': text, 'entities': output_knowledge}

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

def clean_keywords(keywords):
    cleaned_keywords = []
    for kw in keywords:
        kw = kw.lower().strip()

        # Remove unwanted characters: keep +, #, /, and .
        kw = re.sub(r'[()\[\]]', '', kw)  
        kw = kw.replace('\\', '/')       
        kw = re.sub(r'\s*/\s*', '/', kw)  

        parts = re.split(r'[,\n;]|(?<!\w)(?:and|or)(?!\w)|\s{2,}', kw)

        for part in parts:
            part = part.strip()

            if len(part.split()) > 3:
                sub_parts = part.split()
            else:
                sub_parts = [part]

            for item in sub_parts:
                item = item.strip().strip("()[]{}").strip()
                item = re.sub(r'\s+', ' ', item) 

                if item and is_valid_keyword(item):
                    cleaned_keywords.append(item)

    return cleaned_keywords

def omit_unwanted_words(omit, words):
    if not omit:
        return words
    
    omit = [word.strip().lower() for word in omit.split(',') if word.strip()]

    for omit_word in omit:
        pattern = r'\b' + re.escape(omit_word.lower()) + r'\b'
        words = re.sub(pattern, '', words, flags=re.IGNORECASE)

    words = re.sub(r'\s+&\s+', ' ', words)             
    words = re.sub(r'\s+&(?=\W|$)', ' ', words)      
    words = re.sub(r'(?<=\W)&\s+', ' ', words)   
    words = re.sub(r'\s+', ' ', words).strip()

    return words

def process_resume_and_job(file_pdf, job_description_and_skills, job_title, omit_words):
    pdf_path = Path(UPLOAD_FOLDER)
    resume_pdf = (os.listdir(pdf_path))[0]
    resume_text = extract_text_from_pdf(str(UPLOAD_FOLDER + '/' + resume_pdf))
   
    if omit_words:
        job_description_and_skills = omit_unwanted_words(omit_words, job_description_and_skills)

    job_skills_dict, job_knowledge_dict = extract_keywords(job_description_and_skills)
    skills_keywords = [entity['word'].lower() for entity in job_skills_dict['entities'] if is_valid_keyword(entity['word'])]
    knowledge_keywords = [entity['word'].lower() for entity in job_knowledge_dict['entities'] if is_valid_keyword(entity['word'])]
    
    skills_keywords = clean_keywords(skills_keywords)
    knowledge_keywords = clean_keywords(knowledge_keywords)
    job_skills_keywords = skills_keywords + knowledge_keywords

    keyword_score, unmatched_words, matched_keywords = calculate_applicant_resume_match(resume_text, job_skills_keywords)
    print('Applicant Keyword Match: % ' + str(keyword_score * 100))

    similarity_score = (get_similarity(resume_text, job_description_and_skills)) * 100
    print('Applicant Resume To Job Match Score: % ' + str(similarity_score))

    # ai_response, similarity_score_note = applicant_advice(keyword_score, unmatched_words, job_title, similarity_score)

    return {
        'keyword_match': int(keyword_score * 100),
        'matching_keywords': matched_keywords,
        'missing_keywords': unmatched_words,
        'resume_to_job_similarity': int(similarity_score),
        'upskilling_advice': "ai_response"
    }