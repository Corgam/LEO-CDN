FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./gsts/requirements-gsts.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./temp/gsts.csv /gsts.csv
COPY ./temp/file_orders.json /file_orders.json

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./gsts/gsts.py /gsts.py

CMD ["python", "gsts.py"]
