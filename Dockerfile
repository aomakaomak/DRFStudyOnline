FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY="django-insecure-=kdvj_88e6_lhf#kx*3m2f03^8h551(6%*r$&72kuzo!d8)u9!"
ENV CELERY_BROKER_URL="redis://redis:6379/0"
ENV CELERY_BACKEND="redis://redis:6379/0"

RUN mkdir -p /app/media

EXPOSE 8000
