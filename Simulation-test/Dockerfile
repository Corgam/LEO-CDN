FROM python:3.8

COPY ./Simulation-test/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./Simulation-test/keygroup_passer.py /keygroup_passer.py

CMD ["python", "keygroup_passer.py"]
