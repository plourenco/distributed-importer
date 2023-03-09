FROM python:3.11
RUN useradd -ms /bin/bash celery
WORKDIR /app
COPY . /app
RUN chown -R celery:celery /app
USER celery
RUN pip3 install -r requirements.txt
