#!/usr/bin/env bash
set -e
pip install -r requirements.txt
export PORT="${PORT:-8000}"
python main.py
