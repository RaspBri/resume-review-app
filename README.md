# resume-review-app

Python commands to make virtual env
python3 -m venv venv
source venv/bin/activate

Start frontend with go to client first then 'npm start'
Start backend with 'python3 server.py'

Lessons Learned:
- If your localhost port is currently being used, you may get a CORS "No access-control-allow-origin" error. To resolve just increment the port by 1 (ex. port 5000 -> port 5001)

NLP - similarity score vs keyword matching

Adding Gemini AI for career advice in the end

Keeping secrets secrets, aka AWS Secrets Manager

pip freeze > requirements.txt # Command to list all the dependencies required for the Python project
pip install -r requirements.txt # Install all dependencies from req.txt

After updating a file
Frontend run "npm run build" -> docker compose build --no-cache -> docker compose up -d