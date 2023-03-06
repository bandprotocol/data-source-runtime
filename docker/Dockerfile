FROM python:3.9-slim

ENV MAX_EXECUTABLE=8192
ENV MAX_DATA_SIZE=512

WORKDIR /executor

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY executor .

EXPOSE 8000

RUN adduser --system --no-create-home nonroot
USER nonroot

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "10"]
