#!/bin/bash
./export-mongo.py -u testuser

python -mjson.tool dime-events.json > /dev/null && \
    python -mjson.tool dime-elements.json > /dev/null && \
    curl -H "Content-Type: application/json" -u testuser:testuser123 --data @dime-events.json http://localhost:8080/api/data/events; echo
