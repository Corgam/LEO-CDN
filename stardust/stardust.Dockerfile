FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./stardust/requirements-stardust.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./stardust/stardust.py /stardust.py
COPY ./stardust/requests.txt /requests.txt
COPY ./config.toml /config.toml

CMD ["python", "stardust.py"]