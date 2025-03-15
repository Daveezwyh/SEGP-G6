FROM python:3.11.7-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

ENV PYTHONUNBUFFERED=1

WORKDIR /code/autoclean

RUN chmod +x ./wait-for-it.sh