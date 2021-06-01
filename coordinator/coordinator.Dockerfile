FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements-coordinator.txt /requirements-coordinator.txt
RUN pip install -r /requirements-coordinator.txt

COPY ./coordinator_server.py /coordinator_server.py

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./simulation /simulation

COPY ./simulation_with_h3.py /simulation_with_h3.py
COPY ./proto /proto

CMD ["python", "coordinator_server.py", "simulation_with_h3.py"]