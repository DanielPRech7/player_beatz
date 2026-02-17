FROM python:3.13

RUN apt update -y
RUN apt install -y gettext

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/