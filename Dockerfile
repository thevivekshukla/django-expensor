FROM python:3.12-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc build-essential

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

COPY . /code
WORKDIR /code

EXPOSE 8000
