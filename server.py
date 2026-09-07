import os
import json
import sqlite3
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler

def init_db():
    conn = sqlite3.connect(' تو روت بود از روت می‌خونه تا هرگز 404 نده)، ساختار MIME Types برای CSS/JS/SVG رو هم درست ست می‌کنه:
```python
import os
import json
import sqlite3
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler

def init_db():
conn = sqlite3.connect('.execute("INSERT OR IGNORE INTO tasks (id, title, reward) VALUES (1, 'Join Channel', 100)")
c.execute("INSERT OR IGNORE INTO tasks (id, title, reward) VALUES (2, 'Follow Twitter', 150)")
conn.commit()
conn.close()

class MajixHandler(BaseHTTPRequestHandler):
def send_json(self, data, status=200):
self.send_response(status)
self.send_header('Content-Type', 'application/json')
self.send_header('Access-Control-Allow-Origin', '*')
self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
self.send_header('Access-Control-Allow-Headers', 'Content-Type')
self.end_headers()
self.wfile.write(json.dumps(data).encode('utf-8'))

def do_OPTIONS(self):
self.send_response(200)
self.send_header('Access-Control-Allow-Origin', '*')
self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
self.send_header('Access-Control-Allow-Headers', 'Content-Type')
self.end_headers()

def do_GET(self):
if self.path.startswith('/api/me'):
self.send_json({'user': 'Majix User', 'points': 250})
return
elif self.path.startswith('/api/tasks'):
conn = sqlite3.connect('majix.db')
c = conn.cursor()
c.execute("SELECT id, title, reward FROM tasks")
rows = c.fetchall()
conn.close()
tasks = [{'id': r[0], 'title': r[1], 'reward': r[2]} for r in rows]
self.send_json({'tasks': tasks})
return

# هندل کردن فایل‌های استاتیک فرانت
clean_path = self.path.split('?')[0]
if clean_path == '/' or clean_path == '':
target_rel = 'index.html'
else:
target_rel = clean_path.lstrip('/')

# بررسی مسیر در پوشه public یا روت اصلی
candidate_paths = [
os.path.join('public', target_rel),
target_rel
]

file_to_serve = None
for p in candidate_paths:
if os.path.isfile(p):
file_to_serve = p
break

if file_to_serve:
mime_type, _ = mimetypes.guess_type(file_to_serve)
if not mime_type:
mime_type = 'text/html' if file_to_serve.endswith('.html') else 'application/octet-stream'

try:
with open(file_to_serve, 'rb') as f:
content = f.read()
self.send_response(200)
self.send_header('Content-Type', mime_type)
self.send_header('Content-Length', str(len(content)))
self.end_headers()
self.wfile.write(content)
except Exception as e:
self.send_error(500, f"Server Error: {e}")
else:
self.send_error(404, "File Not Found")

def do_POST(self):
if self.path.startswith('/api/tasks/') and self.path.endswith('/complete'):
task_id = self.path.split('/')[3]
self.send_json({'status': 'ok', 'task_id': task_id, 'reward': 100})
return
self.send_error(404)

if __name__ == '__main__':
init_db()
port = int(os.environ.get('PORT', 8000))
server = HTTPServer(('0.0.0.0', port), MajixHandler)
print(f"🚀 Majix Server running on port {port}...")
server.serve_forever()
