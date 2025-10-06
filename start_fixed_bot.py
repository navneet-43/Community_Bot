#!/usr/bin/env python3
import os
import subprocess
import time

# Step 1: Stop any existing bot processes
print("🛑 Stopping any existing bot processes...")
try:
    result = subprocess.run(['pkill', '-f', 'python.*bot.py'], capture_output=True)
    time.sleep(1)
    print("✅ Existing processes stopped")
except:
    print("ℹ️ No existing processes to stop")

# Step 2: Copy the fixed bot to main bot
print("📋 Copying fixed bot to main bot file...")
try:
    os.system("cp bot_fixed_member_join.py bot.py")
    print("✅ Bot file updated")
except Exception as e:
    print(f"❌ Error copying bot file: {e}")

# Step 3: Clean Python cache
print("🧹 Cleaning Python cache...")
os.system("rm -rf __pycache__")
print("✅ Cache cleaned")

# Step 4: Start the fixed bot
print("🚀 Starting fixed bot with enhanced member join logging...")
try:
    # Start bot in background with logging
    os.system("cd /Users/navneetsingh/Desktop/community_bot && source venv/bin/activate && nohup python -u bot.py > bot_fixed.log 2>&1 &")
    time.sleep(3)
    print("✅ Bot started successfully!")
    
    # Check if bot is running
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'bot.py' in result.stdout:
        print("✅ Bot process confirmed running")
        
        # Show initial logs
        print("\n📋 Initial bot logs:")
        try:
            with open('/Users/navneetsingh/Desktop/community_bot/bot_fixed.log', 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:  # Last 10 lines
                    print(f"   {line.strip()}")
        except:
            print("   Log file not ready yet")
    else:
        print("❌ Bot process not found")
        
except Exception as e:
    print(f"❌ Error starting bot: {e}")

print("\n🎯 Bot is ready for testing!")
print("📋 To monitor logs: tail -f /Users/navneetsingh/Desktop/community_bot/bot_fixed.log")
print("🧪 Test by having someone join your Discord server!")
