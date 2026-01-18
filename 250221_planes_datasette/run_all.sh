#!/bin/bash

python3 digest_daily.py convert-day example-data/250125.txt.gz --dest-json /tmp/250125.json
geojson-to-sqlite 250125.db planes /tmp/250125.json

datasette serve 250125.db

