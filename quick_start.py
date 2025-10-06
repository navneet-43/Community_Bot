import os
import subprocess
import time

# Quick bot restart with enhanced member join detection
print("🚀 Quick Starting Fixed Bot...")

# Stop any existing bots
os.system("pkill -f 'python.*bot.py' 2>/dev/null || true")
time.sleep(1)

# Install fixed bot
os.system("cp bot_fixed_member_join.py bot.py")
print("✅ Fixed bot installed")

# Clean and start
os.system("rm -rf __pycache__ && source venv/bin/activate && nohup python -u bot.py > bot_fixed.log 2>&1 &")
time.sleep(2)

print("🎯 Bot started! Check logs with: tail -f bot_fixed.log")
print("🧪 Test by having someone join your Discord server!")
