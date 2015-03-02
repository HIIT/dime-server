#!/bin/bash
curl -X POST -H "Content-Type: application/json" http://localhost:8080/logger \
    -d '{ "name": "BarFoo", "eventType": "created", "time": "2015-03-02T08:11:00Z" }'
echo
