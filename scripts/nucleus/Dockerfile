# Get python slim image
FROM python:3.10-slim-buster

# Setup virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy script file
COPY getVulns.py .
RUN chmod +x getVulns.py

# Code file to execute when the docker container starts up (`entrypoint.sh`)
CMD ["python3","getVulns.py"]
