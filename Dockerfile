FROM python:3.13.5-slim-bookworm AS builder

ARG TZ=America/New_York
RUN apt update && apt -yq install gcc make
RUN \
    pip install requests \
    && pip install influxdb-client \
    && pip cache purge


FROM python:3.13.5-slim-bookworm

ARG TZ=America/New_York
ARG PYVER=3.13

VOLUME [ "/config" ]

COPY --from=builder /usr/local/lib/python$PYVER/site-packages/ /usr/local/lib/python$PYVER/site-packages/

RUN mkdir /app
COPY ./sensorem.py /app
RUN chmod 755 /app/sensorem.py

ENTRYPOINT [ "python3", "-u", "/app/sensorem.py" ]
