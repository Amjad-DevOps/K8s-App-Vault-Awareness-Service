FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y gnupg 
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5003
ENTRYPOINT ["python3", "/app/app.py"]
