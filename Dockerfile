FROM python:3.10

WORKDIR /src
COPY requirements.txt /src
RUN pip install -r requirements.txt
COPY . /src

RUN apt-get update && apt-get install -y apt-transport-https
RUN apt update && apt install ffmpeg -y
RUN apt install sox -y

# RUN apk add  --no-cache ffmpeg

CMD python3 /src/client/authorization.py
CMD python3 /src/app.py
