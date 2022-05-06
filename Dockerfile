FROM python:slim-buster
LABEL org.opencontainers.image.authors="16841946+samkshah@users.noreply.github.com"
WORKDIR /opt/nucleus
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY getVulns.py .
CMD ["python3", "-W ignore","getVulns.py"]