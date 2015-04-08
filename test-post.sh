#!/bin/bash
curl -X POST -H "Content-Type: application/json" -u mats http://localhost:8080/api/data/zgevent \
    -d '{ "actor": "Emacs", "manifestation": "something", "timestamp": "2015-03-02T08:11:00Z" }'

echo
