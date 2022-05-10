# Get python slim image
FROM python

# Setup virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy script file
COPY getVulns.py ./
# Code file to execute when the docker container starts up
RUN ["python3", "./getVulns.py"]