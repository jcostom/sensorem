FROM python:slim

ENV TZ=America/New_York

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN \
    pip3 install requests \
    && pip3 install influxdb-client \
    && pip cache purge

RUN mkdir /app
COPY ./sensorem.py /app
RUN chmod 755 /app/sensorem.py

ENTRYPOINT [ "python3", "-u", "/app/sensorem.py" ]