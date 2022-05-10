# Get python slim image
FROM python:slim-buster

# Setup virtualenv
# ENV VIRTUAL_ENV=/opt/venv
# RUN python3 -m venv $VIRTUAL_ENV
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy script file
COPY test.py .
# Code file to execute when the docker container starts up
ENTRYPOINT [ "sh", "-c", "python3 test.py" ]