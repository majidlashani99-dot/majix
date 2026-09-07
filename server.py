from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3
import urllib.parse
import os
import mimetypes

# مسیر امن و مستقل از محل اجرای دستور
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "majix.db")


def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            balance INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            reward INTEGER,
            type TEXT
        )
    """)

    task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    if task_count == 0:
        conn.executemany(
            "INSERT INTO tasks(title, description, reward, type) VALUES (?, ?, ?, ?)",
            [
                ("تماشای ویدئوی تبلیغاتی", "یک ویدئوی کوتاه را کامل ببینید", 50, "video"),
                ("فالو کردن کانال مجیکس", "کانال تلگرام را دنبال کنید", 100, "social"),
                ("دعوت از یک دوست", "لینک دعوت خود را برای یک دوست ارسال کنید", 250, "invite"),
                ("ورود روزانه", "امروز وارد اپ شوید", 20, "daily"),
            ],
        )

    conn.execute(
        "INSERT OR IGNORE INTO users(id, name, balance) VALUES (?, ?, ?)",
        (1, "مجید", 0),
    )

    conn.commit()
    conn.close()


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status_code=200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        self.wfile.write(raw)

    def send_file(self, request_path):
        # صفحه اصلی
        if request_path == "/":
            request_path = "/index.html"

        # جلوگیری از Path Traversal مانند ../../server.py
        relative_path = os.path.normpath(request_path.lstrip("/"))

        if relative_path.startswith("..") or os.path.isabs(relative_path):
            self.send_error(403, "Forbidden")
            return

        file_path = os.path.join(BASE_DIR, relative_path)

        # فقط فایل‌های موجود در پروژه را سرو می‌کند
        if not os.path.isfile(file_path):
            self.send_error(404, "File not found")
            return

        try:
            with open(file_path, "rb") as file:
                content = file.read()

            content_type, _ = mimetypes.guess_type(file_path)

            if not content_type:
                content_type = "application/octet-stream"

            # برای HTML UTF-8
            if content_type == "text/html":
                content_type = "text/html; charset=utf-8"
            elif content_type == "text/css":
                content_type = "text/css; charset=utf-8"
            elif content_type == "application/javascript":
                content_type = "application/javascript; charset=utf-8"

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        except OSError:
            self.send_error(500, "Could not read file")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        # API: اطلاعات کاربر
        if path == "/api/me":
            conn = sqlite3.connect(DB)
            row = conn.execute(
                "SELECT id, name, balance FROM users WHERE id = 1"
            ).fetchone()
            conn.close()

            if not row:
                return self.send_json({"error": "user not found"}, 404)

            return self.send_json(
                {
                    "id": row[0],
                    "name": row[1],
                    "balance": row[2],
                }
            )

        # API: لیست تسک‌ها
        if path == "/api/tasks":
            conn = sqlite3.connect(DB)
            rows = conn.execute(
                "SELECT id, title, description, reward, type FROM tasks"
            ).fetchall()
            conn.close()

            tasks = [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "reward": row[3],
                    "type": row[4],
                }
                for row in rows
            ]

            return self.send_json(tasks)

        # فایل‌های فرانت‌اند از ریشه پروژه
        return self.send_file(path)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        # نمونه مسیر: /api/tasks/1/complete
        if path.startswith("/api/tasks/") and path.endswith("/complete"):
            parts = path.strip("/").split("/")

            # باید api / tasks / ID / complete باشد
            if len(parts) != 4:
                return self.send_json({"error": "invalid task route"}, 400)

            try:
                task_id = int(parts[ try:
                task_id = int(parts[2])
            except ValueError:
                return self"}, 400)

            conn = sqlite3.connect(DB)

            reward_row = conn.execute(
                "SELECT reward FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

            if not reward_row:
                conn.close()
                return self.send_json({"error": "task not found"}, 404)

            reward = reward_row[0]

            conn.execute(
                "UPDATE0]

            conn.execute(
                "UPDATE users SET balance = balance + ? WHERE id =            conn.commit()

            balance = conn.execute(
                "SELECT balance FROM users WHERE id = 1"
            ).fetchone()[0]

            conn.close()

            return self.send_json(
                {
                    "ok": True,
                    "reward": reward,
                    "balance": balance,
                }
            )

        return self.send_json({"error": "not found"}, 404)


if __namenot found"}, 404)


if __name__ == "__main__":
    init_db()

‌کند
    port = int(os.environ.get("PORT", "8000"))

    print(f"Majix is running on port {port}")

    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

---

## 2) فایل `render.yaml` را با این نسخه جایگزین کن
```yaml
services:
  - type: web
name: majix-demo
runtime: python
plan: free
buildCommand: pip install -r requirements.txt
startCommand: python server.py
envVars:
- key: PYTHON_VERSION
value: 3.11.9

---

## 3) یک فایل جدید به نام `requirements.txt` در ریشه پروژه بساز

چون کد فعلی فقط از کتابخانه‌های داخلی پایتون استفاده می‌کند، محتویات آن می‌تواند خالی باشد.

فایل:

```text
# No external Python dependencies required.

> اگر `requirements.txt` نداشته باشی ولی در `render.yaml` نوشته باشی `pip install -r requirements.txt`، مرحله Build در Render خطا می‌دهد.

---

## 4) ساختار نهایی GitHub) ساختار نهایی GitHub باید این باشد
```text
your-project/
│
 server.py
├── render.yaml
├── requirements.txt
└── README.md

اگر فایل‌های جداگانه‌ای مانند CSS، JS، عکس یا فونت داری، در ریشه یا داخل پوشه‌هایی مثل `assets/` قرار بده:

```text
your-project/
├── index.html
├── assets/
│   ├── style.css
│   ├── app.js
│   └── logo.png
├── server.py
├── render.yaml
└── requirements.txt

کد جدید `server.py` فایل‌های `assets/style.css` و `assets/app.js` را هم سرو می‌کند.

---

## 5) در GitHub انجام بده
```bash
git add server.py render.yaml requirements.txt
git commit -m "Fix Render static file serving and deployment config"
git push origin main

اگر branch اصلی تو `master` است، به‌جای `main` بنویس:

```bash
git push origin master

---

## 6) در Render انجام بده

1. وارد داشبورد Render شو.
2. سرویس Web Service خودت را باز کن.
3. بررسی کن:
   - **Build Command**
```text
pip install -r requirements.txt

