FROM python:3.8

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./FReD /FReD
ENV PYTHONPATH="${PYTHONPATH}:/FReD"

COPY ./keygroup_passer.py /keygroup_passer.py

CMD ["python", "keygroup_passer.py"]
