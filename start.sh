#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Venv létrehozása..."
    python3 -m venv venv
    venv/bin/pip install -q -r requirements.txt
fi

echo "NorcsiAgent indul: http://localhost:8700"
# Telegram token: ~/.sasagent.env fájlból töltjük be
if [ -f "$HOME/.sasagent.env" ]; then
    export $(grep -v '^#' "$HOME/.sasagent.env" | xargs)
fi
venv/bin/python app.py
