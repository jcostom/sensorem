#!/usr/bin/env python3

import os
import json
import logging
import requests
import secrets
from hashlib import sha256
import hmac
from base64 import b64encode
import time
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# --- To be passed in to container ---
# Mandatory Vars
TZ = os.getenv('TOKEN', 'America/New_York')
CONFIG = os.getenv('CONFIG', '/config/config.json')

# Optional Vars
DEBUG = int(os.getenv('DEBUG', 0))

# --- Other Globals ---
VER = '3.2.7'
USER_AGENT = f"sensorem.py/{VER}"
URL = 'https://api.switch-bot.com/v1.1/devices/{}/status'

# Setup logger
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='[%d %b %Y %H:%M:%S %Z]')
logger = logging.getLogger()


def c2f(celsius: float) -> float:
    return (celsius * 9/5) + 32


def build_headers(secret: str, token: str) -> dict:
    nonce = secrets.token_urlsafe()
    t = int(round(time.time() * 1000))
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
    with open(CONFIG, 'r') as f:
        myconfig = json.load(f)
    influxClient = InfluxDBClient(url=myconfig['config']['influx_url'], token=myconfig['config']['influx_token'], org=myconfig['config']['influx_org'])  # noqa: E501
    write_api = influxClient.write_api(write_options=SYNCHRONOUS)
    while True:
        for sensor in myconfig['sensors']:
            (deg_f, rel_hum) = read_sensor(myconfig['sensors'][sensor]['devid'], myconfig['config']['switchbot_secret'], myconfig['config']['switchbot_token'])  # noqa: E501
            record = [
                {
                    "measurement": sensor,
                    "fields": {
                        "degF": deg_f,
                        "rH": rel_hum
                    }
                }
            ]
            write_api.write(bucket=myconfig['config']['influx_bucket'], record=record)  # noqa: E501
        time.sleep(myconfig['config']['sleeptime'])


if __name__ == "__main__":
    main()
