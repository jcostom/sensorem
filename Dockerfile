FROM python:slim

ENV TZ=America/New_York

RUN apt update && apt -yq install curl

RUN \
    pip install requests \
    && pip install influxdb-client \
    && pip cache purge

RUN mkdir /app
COPY ./sensorem.py /app
RUN chmod 755 /app/sensorem.py

HEALTHCHECK --interval=3m --timeout=10s --retries=3 \
    CMD [ "/usr/bin/curl", "-sfo", "/dev/null", "https://api.switch-bot.com/ping" ] || exit 1

ENTRYPOINT [ "python3", "-u", "/app/sensorem.py" ]