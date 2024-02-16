FROM python:3.12-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc build-essential lsb-release wget

# Create the file repository configuration:
RUN sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Import the repository signing key:
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg

RUN apt-get update \
    && apt-get -y install postgresql-client-16

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

COPY . /code
WORKDIR /code

EXPOSE 8000
