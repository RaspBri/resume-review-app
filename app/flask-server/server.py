# TODO: When going to PROD, be sure to switch to PROD server
# https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os, sys, threading, traceback
from werkzeug.utils import secure_filename

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*") # get requests from React frontend

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
    if response is None:
        response = make_response('', 500)
    return add_cors_headers(response)

# TODO: Make constants file 
# TODO: Make the resources upload directory temporary, need to rename to temp

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
UPLOAD_FOLDER = os.path.join(base_dir, 'resources')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# TODO: Set file size limit, prevent DDOS attack of app

@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(Exception)
def handle_all_exceptions(e):
    import traceback
    traceback.print_exc()
    return make_response(jsonify({'error': 'Internal server error'}), 500)

@app.route('/favicon.ico')
def favicon():
    return '', 204

# Upload File API route
@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        return '', 204
    print("[POST] Upload endpoint hit")
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
            if os.path.isfile(filepath):
                os.remove(filepath)

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        results = main.process_resume_and_job(filepath, job_description, job_title, omit_words)

        return jsonify(results), 200

    except Exception as e:
            print('Error:', e)
            traceback.print_exc()
            return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)