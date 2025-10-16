#!/bin/bash
set -e  # Exit if any command fails

# Go to backend folder
cd backend

# Ensure pip and dependencies are installed
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Start the FastAPI app
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
