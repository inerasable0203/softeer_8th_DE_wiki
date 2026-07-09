FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notebooks ./notebooks
COPY data ./data

EXPOSE 8888

ENV JUPYTER_TOKEN=w2m6-token

CMD ["sh", "-c", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token=${JUPYTER_TOKEN} --ServerApp.password=''"]