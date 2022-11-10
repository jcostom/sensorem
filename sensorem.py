#!/usr/bin/env python3

import os
import logging
import requests
from hashlib import sha256
import hmac
from base64 import b64encode
from time import sleep, time
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# --- To be passed in to container ---
# Mandatory Vars
TOKEN = os.getenv('TOKEN')
SECRET = os.getenv('SECRET')
DEVID = os.getenv('DEVID')
SLEEPTIME = int(os.getenv('SLEEPTIME', 300))
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET')
INFLUX_ORG = os.getenv('INFLUX_ORG')
INFLUX_TOKEN = os.getenv('INFLUX_TOKEN')
INFLUX_URL = os.getenv('INFLUX_URL')
INFLUX_MEASUREMENT_NAME = os.getenv('INFLUX_MEASUREMENT_NAME')

# Optional Vars
DEBUG = int(os.getenv('DEBUG', 0))

# --- Other Globals ---
VER = '2.1'
USER_AGENT = f"sensorem.py/{VER}"
URL = 'https://api.switch-bot.com/v1.1/devices/{}/status'

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


def c2f(celsius: float) -> float:
    return (celsius * 9/5) + 32


def build_headers(secret: str, token: str) -> dict:
    nonce = ''
    t = int(round(time() * 1000))
    string_to_sign = f'{token}{t}{nonce}'
    b_string_to_sign = bytes(string_to_sign, 'utf-8')
    b_secret = bytes(secret, 'utf-8')
    sign = b64encode(hmac.new(b_secret, msg=b_string_to_sign, digestmod=sha256).digest())  # noqa: E501
    headers = {
        'Authorization': token,
        't': str(t),
        'sign': sign,
        'nonce': nonce
    }
    return headers


def build_url(url_template: str, devid: str) -> str:
    return url_template.format(devid)


def read_sensor(devid: str, secret: str, token: str) -> list:
    url = build_url(URL, devid)
    headers = build_headers(secret, token)
    r = requests.get(url, headers=headers)
    return [round(c2f(r.json()['body']['temperature']), 1), r.json()['body']['humidity']]  # noqa: E501


def main() -> None:
    logger.info(f"Startup: {USER_AGENT}")
    influxClient = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)  # noqa: E501
    write_api = influxClient.write_api(write_options=SYNCHRONOUS)
    while True:
        (deg_f, rel_hum) = read_sensor(DEVID, SECRET, TOKEN)
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
