# pull from image base
FROM python:3.8.3-slim
#RUN apk add --update --no-cache curl py-pip
#RUN apk --update add build-base libffi-dev openssl-dev python-dev py-pip

WORKDIR .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install python3-dev -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install libglib2.0-0 -y
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# create staticfile dirs
#ENV HOME=/var/www/html
#ENV APP_HOME=/var/www/html/smart-office
#RUN mkdir -p $APP_HOME
#RUN mkdir -p $APP_HOME/static
#RUN mkdir -p $APP_HOME/media
#WORKDIR $APP_HOME

# copy the project
COPY . .