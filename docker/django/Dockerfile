FROM python:3.7.4-alpine

ARG DJANGO_ENV
ARG APP_PORT=8000

ENV DJANGO_ENV=${DJANGO_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on

ENV DJANGO_SETTINGS_MODULE=expensor.settings.${DJANGO_ENV}
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:$APP_PORT --workers=5"

WORKDIR /app

RUN apk --no-cache add \
     bash \
     curl \
     gcc \
     gettext \
     git \
     libffi-dev \
     musl-dev \
     postgresql-dev

COPY . .

RUN pip install -r requirements/$DJANGO_ENV.txt

CMD gunicorn expensor.wsgi
