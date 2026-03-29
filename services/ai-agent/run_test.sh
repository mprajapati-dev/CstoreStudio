#!/bin/sh
export GEMINI_API_KEY=$(cat .env | grep GEMINI_API_KEY | cut -d '=' -f2)
python test_cloud_model.py
