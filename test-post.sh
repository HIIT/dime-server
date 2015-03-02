#!/bin/bash
curl -X POST -H "Content-Type: application/json" http://localhost:8080/logger -d @json
echo
