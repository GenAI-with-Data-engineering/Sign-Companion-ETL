FROM python:3.10.6-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY streamlit/ /app/streamlit/
COPY requirements.txt /app/requirements.txt
COPY data/ /app/data/
COPY .env /app/.env

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
