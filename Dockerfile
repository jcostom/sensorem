FROM python:slim

ARG TZ=America/New_York

RUN \
    pip install requests \
    && pip install influxdb-client \
    && pip cache purge

RUN mkdir /app
COPY ./sensorem.py /app
RUN chmod 755 /app/sensorem.py

ENTRYPOINT [ "python3", "-u", "/app/sensorem.py" ]