# resume-review-app

Python commands to make virtual env
python3 -m venv venv
source venv/bin/activate

Start frontend with 'npm start'
Start backend with 'python3 server.py'

Lessons Learned:
- If your localhost port is currently being used, you may get a CORS "No access-control-allow-origin" error. To resolve just increment the port by 1 (ex. port 5000 -> port 5001)