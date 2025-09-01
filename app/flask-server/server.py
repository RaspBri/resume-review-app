# TODO: When going to PROD, be sure to switch to PROD server
# https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen

from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys, threading
from werkzeug.utils import secure_filename

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

app = Flask(__name__)
# CORS(app) # get requests from React frontend

FRONTEND_URL = "http://localhost:3000"

def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin  # Adjust as needed
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response

@app.after_request
def after_request(response):
    return add_cors_headers(response)

# TODO: Make constants file 
# TODO: Make the resources upload directory temporary, need to rename to temp

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
UPLOAD_FOLDER = os.path.join(base_dir, 'resources')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# TODO: Set file size limit, prevent DDOS attack of app

# Upload File API route
@app.route('/upload', methods=['POST'])
def upload():
    try: 
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        job_description = request.form.get('job_description')
        job_title = request.form.get('job_title')
        omit_words = request.form.get('omit_words')

        if not job_description:
             return jsonify({'error': 'No job desciption provided.'})

        filename = secure_filename(file.filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(UPLOAD_FOLDER):
                os.remove(UPLOAD_FOLDER)

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # results = threading.Thread(target=main.process_resume_and_job, args=((filepath + '/' + filename), job_description, job_title)).start()
        results = main.process_resume_and_job((filepath + '/' + filename), job_description, job_title, omit_words)

        response = jsonify({'message': 'File and job description recieved successfully', 'filename': file.filename})
        return jsonify(results)

    except Exception as e:
            print('Error:', e)
            return jsonify({'error': 'Server error'}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)