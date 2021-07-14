FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y libgrpc-dev python3-dev default-libmysqlclient-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-satellite.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY satellite_server.py /satellite_server.py
COPY fred_client.py /fred_client.py
COPY satellite.py /satellite.py
COPY Request.py /Request.py
COPY proto /proto

RUN mkdir logs
RUN mkdir data

CMD ["python", "satellite_server.py"]
