FROM python:slim-buster
LABEL org.opencontainers.image.authors="16841946+samkshah@users.noreply.github.com"

# Install dependencies
WORKDIR /opt/app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application
COPY getVulns.py .
CMD ["python", "getVulns.py"]