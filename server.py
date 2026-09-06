from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
import os
import sqlite3
import urllib.parse

DB = "majix.db"


def init_db():
    c = sqlite3.connect(DB)
    c.execute(
        "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, balance INTEGER DEFAULT 0)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, title TEXT, description TEXT, reward INTEGER, type TEXT)"
    )
    if c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO tasks(title,description,reward,type) VALUES(?,?,?,?)",
            [
                (
                    "تماشای ویدئوی تبلیغاتی",
                    "یک ویدئوی کوتاه را کامل ببینید",
                    50,
                    "video",
                ),
                (
                    "فالو کردن کانال مجیکس",
                    "کانال تلگرام را دنبال کنید",
                    100,
                    "social",
                ),
                (
                    "دعوت از یک دوست",
                    "لینک دعوت خود را برای یک دوست ارسال کنید",
                    250,
                    "invite",
                ),
                ("ورود روزانه", "امروز وارد اپ شوید", 20, "daily"),
            ],
        )
    c.execute("INSERT OR IGNORE INTO users(id,name,balance) VALUES(1,'مجید',0)")
    c.commit()
    c.close()


class Handler(BaseHTTPRequestHandler):

    def out(self, data, code=200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/me":
            c = sqlite3.connect(DB)
            r = c.execute("SELECT id,name,balance FROM users WHERE id=1").fetchone()
            c.close()
            return self.out(dict(zip(["id", "name", "balance"], r)))

        if path == "/api/tasks":
            c = sqlite3.connect(DB)
            rows = c.execute(
                "SELECT id,title,description,reward,type FROM tasks"
            ).fetchall()
            c.close()
            return self.out(
                [
                    dict(zip(["id", "title", "description", "reward", "type"], r))
                    for r in rows
                ]
            )

        if path == "/":
            path = "/index.html"

        file_path = os.path.join("public", path.lstrip("/"))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"

            with open(file_path, "rb") as f:
                raw = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(raw)
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path.startswith("/api/tasks/") and path.endswith("/complete"):
            try:
                tid = int(path.split("/")[3])
                c = sqlite3.connect(DB)
                reward = c.execute(
                    "SELECT reward FROM tasks WHERE id=?", (tid,)
                ).fetchone()
                if not reward:
                    c.close()
                    return self.out({"error": "task not found"}, 404)

                c.execute(
                    "UPDATE users SET balance=balance+? WHERE id=1", (reward[0],)
                )
                c.commit()
                bal = c.execute(
                    "SELECT balance FROM users WHERE id=1"
                ).fetchone()[0]
                c.close()
                return self.out({"ok": True, "reward": reward[0], "balance": bal})
            except Exception as e:
                return self.out({"error": str(e)}, 500)

        return self.out({"error": "not found"}, 404)


if __name__ == "__main__":
    init_db()
    # دریافت پورت از متغیرهای محیطی رندر (پیش‌فرض 10000)
    port = int(os.environ.get("PORT", 10000))
    # گوش دادن روی تمام اینترفیس‌ها با 0.0.0.0
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, Handler)
    print(f"Majix server running on port {port}...")
    httpd.serve_forever()
