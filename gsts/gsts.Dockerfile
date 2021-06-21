FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./gsts/requirements-gsts.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./gsts/gsts.py /gsts.py
COPY ./temp/gsts.txt /gsts.txt

CMD ["python", "gsts.py"]