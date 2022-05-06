FROM python:slim-buster
LABEL org.opencontainers.image.authors="16841946+samkshah@users.noreply.github.com"
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY getVulns.py .
RUN chmod +x getVulns.py
RUN ls -lag
ENTRYPOINT [ "getVulns.py" ]