import sqlite3
from datetime import datetime

# создаём базу, если нет
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    category TEXT,
    date TEXT
)
""")
conn.commit()

def add_expense(user_id: int, amount: float, category: str):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
        (user_id, amount, category, date)
    )
    conn.commit()

def get_expenses(user_id: int):
    cursor.execute(
        "SELECT amount, category, date FROM expenses WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    return cursor.fetchall()

def get_stats(user_id: int):
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 3",
        (user_id,)
    )
    return cursor.fetchall()
