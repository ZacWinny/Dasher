FROM python:3.10-slim-buster

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt
# # Install dos2unix and convert the line endings of the script
# RUN apt-get update && apt-get install -y dos2unix
# RUN dos2unix ./docker_script.sh && chmod +x ./docker_script.sh
RUN pip install pytest pytest-xdist pytest-cov

EXPOSE 5000

CMD ["./docker_script.sh"]