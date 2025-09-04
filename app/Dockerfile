FROM python:3.11-slim

WORKDIR /app

# Copy proj files into container
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 5001 for Flask
EXPOSE 5001

CMD ["python3", "flask-server/server.py"]