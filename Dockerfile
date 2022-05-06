FROM python:slim-buster
LABEL org.opencontainers.image.authors="16841946+samkshah@users.noreply.github.com"

# Setup virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application
COPY getVulns.py .
CMD ["python3", "getVulns.py"]