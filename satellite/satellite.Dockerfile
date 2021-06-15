FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-satellite.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY satellite_server.py /satellite_server.py
COPY satellite.py /satellite.py
COPY fred_communication.py /fred_communication.py
COPY satellite_movement.py /satellite_movement.py
COPY proto /proto
RUN mkdir /logs

CMD ["python", "satellite_server.py"]
