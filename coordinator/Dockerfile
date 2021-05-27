FROM python:3.8-alpine
COPY ./coordinator/requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY ./coordinator/coordinator_server.py /coordinator_server.py
COPY ./coordinator/coordinator_client.py /coordinator_client.py
ENV FLASK_APP=coordinator_server
EXPOSE 5000
CMD ["flask", "run"]