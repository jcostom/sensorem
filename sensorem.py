#!/usr/bin/env python3

import os
import logging
import requests
from time import sleep
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

APIKEY = os.getenv('APIKEY')
DEVID = os.getenv('DEVID')
sleepTime = int(os.getenv('sleepTime', 300))
influxBucket = os.getenv('influxBucket')
influxOrg = os.getenv('influxOrg')
influxToken = os.getenv('influxToken')
influxURL = os.getenv('influxURL')
influxMeasurementName = os.getenv('influxMeasurementName')
DEBUG = int(os.getenv('DEBUG', 0))

VER = '1.9'
USER_AGENT = "/".join(['sensorem.py', VER])

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


def readSensor(sbURL, sbHeaders):
    r = requests.get(sbURL, headers=sbHeaders)
    # return array of (degF, rHum)
    return (round(c2f(r.json()['body']['temperature']), 1),
            r.json()['body']['humidity'])


def main():
    logger.info(f"Startup: {USER_AGENT}")
    url = "/".join(
        ("https://api.switch-bot.com/v1.0/devices",
         DEVID,
         "status")
    )
    headers = {'Authorization': APIKEY}
    influxClient = InfluxDBClient(url=influxURL, token=influxToken,
                                  org=influxOrg)
    write_api = influxClient.write_api(write_options=SYNCHRONOUS)
    while True:
        (degF, rH) = readSensor(url, headers)
        record = [
            {
                "measurement": influxMeasurementName,
                "fields": {
                    "degF": degF,
                    "rH": rH
                }
            }
        ]
        write_api.write(bucket=influxBucket, record=record)
        sleep(sleepTime)


if __name__ == "__main__":
    main()
