FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./satellite/requirements-satellite.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./satellite/satellite_server.py /satellite_server.py
COPY ./satellite/proto /proto

CMD ["python", "satellite_server.py"]
