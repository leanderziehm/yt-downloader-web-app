FROM docker.io/library/python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .
COPY static/ ./static/
COPY templates/ ./templates/

# Flask listens on port 5000
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]