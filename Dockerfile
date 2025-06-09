# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# default to running the prediction service
ENV USE_MQTT=1
ENV USE_AWS=0

CMD ["python", "predict.py"]
