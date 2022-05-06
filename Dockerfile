FROM python:latest
LABEL org.opencontainers.image.authors="16841946+samkshah@users.noreply.github.com"

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application
COPY getVulns.py test.py ./
RUN chmod +x test.py
ENTRYPOINT [ "test.py" ]