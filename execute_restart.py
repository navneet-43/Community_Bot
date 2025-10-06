#!/usr/bin/env python3
"""
Execute the bot restart process
"""

import os
import signal
import subprocess
import time

def stop_bot():
    """Stop any running bot processes"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        killed = 0
        for line in lines:
            if 'python' in line and 'bot.py' in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    print(f"🛑 Killing bot process: {pid}")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        killed += 1
                    except:
                        pass
        
        if killed > 0:
            print(f"✅ Stopped {killed} bot process(es)")
            time.sleep(2)
        else:
            print("ℹ️ No bot processes found")
            
    except Exception as e:
        print(f"❌ Error stopping bot: {e}")

def start_bot():
    """Start the fixed bot"""
    print("🚀 Starting fixed bot with enhanced member join logging...")
    
    # Copy fixed bot to main bot
    result = os.system("cp bot_fixed_member_join.py bot.py")
    if result == 0:
        print("✅ Copied fixed bot to main bot file")
    else:
        print("❌ Failed to copy bot file")
        return
    
    # Clean cache
    os.system("rm -rf __pycache__")
    print("🧹 Cleaned Python cache")
    
    # Start bot in background
    result = os.system("source venv/bin/activate && nohup python -u bot.py > bot_fixed.log 2>&1 &")
    if result == 0:
        print("✅ Bot started in background")
    else:
        print("❌ Failed to start bot")
        return
    
    print("\n📋 Bot Status:")
    time.sleep(2)
    
    # Check if bot is running
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'python.*bot.py' in result.stdout:
        print("✅ Bot is running successfully!")
    else:
        print("❌ Bot may not be running properly")
    
    print("\n📋 To monitor the bot:")
    print("   tail -f bot_fixed.log")
    print("\n🎯 Now test by having someone join your Discord server!")

if __name__ == "__main__":
    stop_bot()
    start_bot()
