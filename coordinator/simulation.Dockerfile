FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements-container.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./simulation /simulation

COPY ./simulation_with_h3.py /simulation_with_h3.py
COPY ./proto /proto

CMD ["python", "simulation_with_h3.py"]
