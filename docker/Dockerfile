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

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "--workers", "32", "--timeout", "0"]

# FOR TESTING ONLY
# CMD ["uvicorn","app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
