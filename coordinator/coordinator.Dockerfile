FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./coordinator_server.py /coordinator_server.py

CMD ["python", "coordinator_server.py"]