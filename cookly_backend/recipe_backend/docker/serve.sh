#!/bin/sh

cd src

if [ "$DEBUG" = "1" ]; then
    echo "Running in dev mode with reload"
    uvicorn presentation.web_api.main:app --host 0.0.0.0 --port 8080 --reload --forwarded-allow-ips='*' --proxy-headers
else
    python3 -m presentation.web_api.main
fi
