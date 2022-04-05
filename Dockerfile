FROM python:3.9-alpine

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

COPY *.py /app/
CMD ["python", "aldi.py"]