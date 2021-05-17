FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements-container.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./keygroup_passer.py /keygroup_passer.py
COPY ./proto /proto

CMD ["python", "keygroup_passer.py"]
