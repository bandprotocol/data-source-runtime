FROM python:3.9-slim-buster

WORKDIR /executor
COPY docker-executor /executor

ENV MAX_EXECUTABLE=8192
ENV MAX_DATA_SIZE=512

EXPOSE 5000

RUN pip3 install -r requirements.txt
RUN chmod 750 .

CMD [ "gunicorn", "app:app", "-b", "0.0.0.0:5000", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "48", "--timeout", "30"]
