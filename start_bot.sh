#!/bin/bash

echo "🛑 Stopping any existing bot instances..."
killall -9 Python 2>/dev/null
pkill -9 -f "python.*bot.py" 2>/dev/null
sleep 2

echo "🧹 Cleaning Python cache..."
cd /Users/navneetsingh/Desktop/community_bot
rm -rf __pycache__
rm -f *.pyc

echo "✅ Verifying config..."
source venv/bin/activate
python3 -c "import config; print(f'City options: {len(config.SCREENING_QUESTIONS[\"city\"][\"options\"])}')"

echo "🚀 Starting bot..."
python bot.py
