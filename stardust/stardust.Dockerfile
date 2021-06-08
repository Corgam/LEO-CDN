FROM python:3.8

RUN apt update && \
    apt install -y libgrpc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-stardust.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY stardust.py /stardust.py
COPY requests.txt /requests.txt

CMD ["python", "stardust.py"]