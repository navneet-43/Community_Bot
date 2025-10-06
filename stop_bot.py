#!/usr/bin/env python3
import os
import signal
import subprocess

# Find and kill bot processes
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    for line in lines:
        if 'python' in line and 'bot.py' in line:
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]
                print(f"Killing bot process: {pid}")
                os.kill(int(pid), signal.SIGTERM)
    
    print("Bot processes stopped")
except Exception as e:
    print(f"Error: {e}")
