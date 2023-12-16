FROM python:3.10.6-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY data/ /app/data/
COPY api/ /app/api/
COPY requirements.txt /app/requirements.txt
COPY .env /app/.env


RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y libgl1-mesa-glx ffmpeg


EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
