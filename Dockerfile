# Get python slim image
FROM python:3.10-slim-buster

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy script file
COPY getVulns.py .

# Code file to execute when the docker container starts up (`entrypoint.sh`)
CMD ["python3","test.py"]