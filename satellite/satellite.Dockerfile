FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-satellite.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY satellite_server.py /satellite_server.py
COPY fred_client.py /fred_client.py
COPY satellite.py /satellite.py
COPY Request.py /Request.py
COPY files.csv /files.csv
COPY proto /proto
RUN mkdir logs
RUN mkdir data

RUN sudo apt-get -y update
RUN sudo apt-get -y upgrade
RUN sudo apt-get install -y sqlite3 libsqlite3-dev
RUN /usr/bin/sqlite3 /data/satellite.db

CMD ["python", "satellite_server.py"]
