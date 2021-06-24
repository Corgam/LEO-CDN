FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./coordinator/requirements-coordinator.txt /requirements-coordinator.txt
RUN pip install -r /requirements-coordinator.txt

COPY ./coordinator /coordinator

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./common/cert/ /common/cert/
COPY ./temp /temp

CMD ["python", "coordinator/coordinator_server.py"]