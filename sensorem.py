#!/usr/bin/env python3

import os
import logging
import requests
from time import sleep
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

APIKEY = os.getenv('APIKEY')
DEVID = os.getenv('DEVID')
SLEEPTIME = int(os.getenv('SLEEPTIME', 300))
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET')
INFLUX_ORG = os.getenv('INFLUX_ORG')
INFLUX_TOKEN = os.getenv('INFLUX_TOKEN')
INFLUX_URL = os.getenv('INFLUX_URL')
INFLUX_MEASUREMENT_NAME = os.getenv('INFLUX_MEASUREMENT_NAME')
DEBUG = int(os.getenv('DEBUG', 0))

VER = '1.12'
USER_AGENT = f"sensorem.py/{VER}"

# Setup logger
logger = logging.getLogger()
ch = logging.StreamHandler()
if DEBUG:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')
ch.setFormatter(formatter)
logger.addHandler(ch)


def c2f(celsius):
    return (celsius * 9/5) + 32


def read_sensor(switchbot_url: str, switchbot_headers: dict) -> list:
    r = requests.get(switchbot_url, headers=switchbot_headers)
    # return array of (deg_f, rel_hum)
    return [round(c2f(r.json()['body']['temperature']), 1),
            r.json()['body']['humidity']]


def main():
    logger.info(f"Startup: {USER_AGENT}")
    url = f"https://api.switch-bot.com/v1.0/devices/{DEVID}/status"
    headers = {'Authorization': APIKEY}
    influxClient = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN,
                                  org=INFLUX_ORG)
    write_api = influxClient.write_api(write_options=SYNCHRONOUS)
    while True:
        (deg_f, rel_hum) = read_sensor(url, headers)
        record = [
            {
                "measurement": INFLUX_MEASUREMENT_NAME,
                "fields": {
                    "degF": deg_f,
                    "rH": rel_hum
                }
            }
        ]
        write_api.write(bucket=INFLUX_BUCKET, record=record)
        sleep(SLEEPTIME)


if __name__ == "__main__":
    main()
