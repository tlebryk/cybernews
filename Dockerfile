FROM python:3.9-slim

COPY requirements.txt /

RUN apt-get update && \
      apt-get -y install sudo
RUN sudo apt-get install libgomp1
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt


COPY . .

ENTRYPOINT ["python3", "app.py"]

# CMD []

