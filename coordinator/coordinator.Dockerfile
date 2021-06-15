FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./coordinator/requirements-coordinator.txt /requirements-coordinator.txt
RUN pip install -r /requirements-coordinator.txt

COPY ./coordinator /coordinator

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./satellite /satellite
COPY ./satellite/proto /proto
COPY ./satellite/fred_communication.py /fred_communication.py
COPY ./common/cert/ /common/cert/

CMD ["python", "coordinator/setup_simulation.py"]