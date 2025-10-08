#!/usr/bin/env python3
"""
Simple HTTP server for health checks - required by Render.com
This runs alongside the Discord bot to satisfy Render's port requirements.
"""

import os
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import time

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/health']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Discord Bot is running!')
        else:
            self.send_response(404)
            self.end_headers()

def start_http_server():
    """Start HTTP server on the port specified by Render"""
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"HTTP server starting on port {port}")
    server.serve_forever()

def start_discord_bot():
    """Start the Discord bot"""
    print("Starting Discord bot...")
    subprocess.run(['python', 'bot.py'])

if __name__ == "__main__":
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Wait a moment for HTTP server to start
    time.sleep(2)
    
    # Start Discord bot in main thread
    start_discord_bot()
