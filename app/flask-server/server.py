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
@app.route('/upload-resume', methods=['POST'])
def uploadResume():
    try: 
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        response = jsonify({'message': 'File uploaded successfully', 'filename': file.filename})
        threading.Thread(target=main.extract_text_from_pdf(filepath), args=((filepath + '/' + filename))).start()
        return response

    except Exception as e:
            print('Error:', e)
            return jsonify({'error': 'Server error'}), 500


# Upload Job Posting URL
@app.route('/upload-job', methods=['POST'])
def uploadJob():
    try:
        data = request.get_json()
        url = None

        if data and 'url' in data:
            url = data['url']
        elif 'url' in request.form:
            url = request.form['url']

        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        response = jsonify({'message': 'URL received', 'url': url})
        threading.Thread(target=main.extract_text_from_url, args=(url,)).start()

        return response

    except Exception as e:
            print('Error:', e)
            return jsonify({'error': 'Server error'}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)