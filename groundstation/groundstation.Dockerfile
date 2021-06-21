FROM python:3.8

COPY ./groundstation/requirements-groundstation.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY ./data /data

ENV PYTHONPATH="${PYTHONPATH}:/groundstation"
COPY ./groundstation /groundstation

CMD ["python", "-m", "groundstation.simulation", "/data/worldcities.csv", "/data/file_orders.json"]
