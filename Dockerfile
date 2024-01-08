FROM python:3.7.4-slim-buster

WORKDIR /logical_coupling

ADD . /logical_coupling

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]