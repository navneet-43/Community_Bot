#!/usr/bin/env python3
import os
import subprocess
import time

print("🚀 Starting Fixed Discord Bot with Enhanced Member Join Detection")
print("=" * 60)

# Stop existing processes
print("🛑 Step 1: Stopping existing bot processes...")
os.system("pkill -f 'python.*bot.py' 2>/dev/null || true")
time.sleep(2)
print("✅ Existing processes stopped")

# Copy fixed bot
print("📋 Step 2: Installing fixed bot...")
os.system("cp bot_fixed_member_join.py bot.py")
print("✅ Fixed bot installed")

# Clean cache
print("🧹 Step 3: Cleaning cache...")
os.system("rm -rf __pycache__ *.pyc")
print("✅ Cache cleaned")

# Start bot
print("🚀 Step 4: Starting fixed bot...")
os.system("source venv/bin/activate && nohup python -u bot.py > bot_fixed.log 2>&1 &")
time.sleep(3)

# Verify bot is running
print("🔍 Step 5: Verifying bot status...")
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'bot.py' in result.stdout:
    print("✅ Bot is running successfully!")
    
    # Show recent logs
    print("\n📋 Recent bot logs:")
    try:
        with open('bot_fixed.log', 'r') as f:
            lines = f.readlines()
            for line in lines[-8:]:
                print(f"   {line.strip()}")
    except:
        print("   Logs not ready yet")
else:
    print("❌ Bot failed to start")

print("\n" + "=" * 60)
print("🎯 BOT IS READY FOR TESTING!")
print("📋 Monitor logs: tail -f bot_fixed.log")
print("🧪 Test: Have someone join your Discord server")
print("📱 Expected: Auto welcome message + 4-question screening")
print("=" * 60)
