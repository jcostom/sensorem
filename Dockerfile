FROM python:slim

ENV TZ=America/New_York

RUN \
    pip3 install requests \
    && pip3 install influxdb-client

RUN mkdir /app
COPY ./sensorem.py /app
RUN chmod 755 /app/sensorem.py

ENTRYPOINT [ "python3", "-u", "/app/sensorem.py" ]