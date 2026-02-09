import sqlite3
from datetime import datetime

# соединение с базой (файл создаётся сам)
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# создаём таблицу расходов с датой
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    category TEXT,
    date TEXT
)
""")
conn.commit()

# добавить расход с датой
def add_expense(user_id, amount, category):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
        (user_id, amount, category, date)
    )
    conn.commit()

# получить все расходы пользователя
def get_expenses(user_id):
    cursor.execute(
        "SELECT amount, category, date FROM expenses WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    return cursor.fetchall()

# статистика по категориям
def get_stats(user_id):
    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    WHERE user_id = ?
    GROUP BY category
    """, (user_id,))
    return cursor.fetchall()

# удалить все расходы пользователя
def clear_expenses(user_id):
    cursor.execute(
        "DELETE FROM expenses WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
