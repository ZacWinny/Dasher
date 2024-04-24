FROM python:3.10-slim-buster

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]