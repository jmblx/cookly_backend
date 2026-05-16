#!/bin/sh

cd src && \
uvicorn presentation.web_api.main:create_production_app \
  --factory \
  --host 0.0.0.0 \
  --reload
  --proxy-headers