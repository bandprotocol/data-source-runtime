FROM python:3.8-slim-buster

WORKDIR /executor
COPY docker-executor /executor

ENV MAX_EXECUTABLE=8192
ENV MAX_DATA_SIZE=512

EXPOSE 5000

RUN pip3 install -r requirements.txt

CMD [ "gunicorn", "app:app", "-b", "0.0.0.0:5000"]
