#!/usr/bin/env python3
"""
Oracle v2.3 Development Server
Simple HTTP server with CORS support for local testing
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent

class OracleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Enable CORS for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # Custom logging format
        print(f"[ORACLE] {self.address_string()} - {format % args}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), OracleHTTPRequestHandler) as httpd:
        print(f"""
╔════════════════════════════════════════════╗
║   Oracle v2.3 Development Server          ║
║   Governance-First Architecture           ║
╚════════════════════════════════════════════╝

Server running at:
  → http://localhost:{PORT}
  → http://127.0.0.1:{PORT}

Press Ctrl+C to stop
        """)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n[ORACLE] Server stopped by user")
