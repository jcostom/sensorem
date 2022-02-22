#!/usr/bin/python3

import os
import time
import requests
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


def c2f(celsius):
    return (celsius * 9/5) + 32


def readSensor(sbURL, sbHeaders):
    r = requests.get(sbURL, headers=sbHeaders)
    # return array of (degF, rHum)
    return (round(c2f(r.json()['body']['temperature']), 1),
            r.json()['body']['humidity'])


def writeLogEntry(message, status):
    print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime())
          + " {}: {}".format(message, status))


def main():
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
        time.sleep(sleepTime)


if __name__ == "__main__":
    main()
