from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import os
import tempfile

app = Flask(__name__)

# Fall back to a writable temp dir if /data isn't available
_default_db = "/data/expenses.db"
try:
    os.makedirs("/data", exist_ok=True)
    # Quick write-test
    with open("/data/.writable", "w") as f:
        f.write("ok")
    os.unlink("/data/.writable")
except OSError:
    _default_db = os.path.join(tempfile.gettempdir(), "expenses.db")

DB_PATH = os.environ.get("DB_PATH", _default_db)


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submitter TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


CATEGORIES = [
    "Travel", "Meals & Entertainment", "Office Supplies",
    "Software & Subscriptions", "Training & Development",
    "Marketing", "Utilities", "Other"
]


@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES)


@app.route("/api/expenses", methods=["GET"])
def list_expenses():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM expenses ORDER BY date DESC, created_at DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()
    required = ["submitter", "amount", "category", "date"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400
    try:
        amount = float(data["amount"])
        if amount <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Amount must be a positive number"}), 400

    with get_db() as conn:
        conn.execute(
            """INSERT INTO expenses (submitter, amount, category, date, description, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data["submitter"].strip(),
                amount,
                data["category"],
                data["date"],
                data.get("description", "").strip(),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
    return jsonify({"status": "ok"}), 201


@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    with get_db() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
    return jsonify({"status": "deleted"})


@app.route("/api/summary", methods=["GET"])
def summary():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC"
        ).fetchall()
        total = conn.execute("SELECT SUM(amount) as grand_total FROM expenses").fetchone()
    return jsonify({
        "by_category": [dict(r) for r in rows],
        "grand_total": total["grand_total"] or 0.0
    })


# Health endpoint — no DB dependency so it always responds
@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


# Initialise DB on startup (after app is defined)
with app.app_context():
    try:
        init_db()
    except Exception as e:
        app.logger.warning(f"init_db skipped: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
