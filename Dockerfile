FROM ubuntu:latest

USER root

RUN apt update && apt upgrade -y
RUN apt install -y python3-pip ffmpeg

COPY requirements.txt requirements.txt
RUN pip3 install -U -r requirements.txt

WORKDIR /flask

COPY . .

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8081"]
