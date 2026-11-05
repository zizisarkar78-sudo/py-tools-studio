
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
import os
app.secret_key = 
os.environ.get("SECRET_KEY")
DATABASE = "expense.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

init_db()
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "running"}


@app.route("/expense-tracker", methods=["GET","POST"])
def expense_tracker():

    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        amount_text = request.form.get("amount", "").strip()

        try:
            amount = float(amount_text)

            if not name:
                raise ValueError("Please enter a transaction name.")

            if category not in ["income", "expense"]:
                raise ValueError("Invalid transaction type.")

            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            with get_db() as conn:
                conn.execute(
                    """INSERT INTO transactions
                    (name, amount, category)
                    VALUES (?, ?, ?)""",
                    (name, amount, category)
                )

            return redirect(url_for("expense_tracker"))

        except ValueError as e:
            error = str(e)

    with get_db() as conn:
        transactions = conn.execute(
            "SELECT * FROM transactions ORDER BY id DESC"
        ).fetchall()

        income = conn.execute(
            "SELECT SUM(amount) FROM transactions WHERE category='income'"
        ).fetchone()[0] or 0

        expenses = conn.execute(
            "SELECT SUM(amount) FROM transactions WHERE category='expense'"
        ).fetchone()[0] or 0

    balance = income - expenses

    return render_template(
        "expense_tracker.html",
        transactions=transactions,
        income=income,
        expenses=expenses,
        balance=balance,
        error=error
    )


@app.route("/delete-transaction/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):

    with get_db() as conn:
        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

    return redirect(url_for("expense_tracker"))


@app.route("/marks-calculator", methods=["GET", "POST"])
def marks_calculator():

    result = None
    error = None

    if request.method == "POST":
        name = request.form.get("student_name", "").strip()

        subjects = ["English", "Bengali", "Math", "Science", "History"]

        try:
            if not name:
                raise ValueError("Please enter student name.")

            marks = []

            for subject in subjects:
                value = float(request.form.get(subject, ""))

                if not 0 <= value <= 100:
                    raise ValueError(
                        f"{subject} marks must be between 0 and 100."
                    )

                marks.append(value)

            total = sum(marks)
            percentage = total / 5

            if any(mark < 33 for mark in marks):
                grade = "F"
                status = "FAIL"
            elif percentage >= 90:
                grade = "A+"
                status = "PASS"
            elif percentage >= 80:
                grade = "A"
                status = "PASS"
            elif percentage >= 70:
                grade = "B"
                status = "PASS"
            elif percentage >= 60:
                grade = "C"
                status = "PASS"
            elif percentage >= 50:
                grade = "D"
                status = "PASS"
            else:
                grade = "E"
                status = "PASS"

            result = {
                "name": name,
                "subjects": subjects,
                "marks": marks,
                "total": total,
                "percentage": percentage,
                "grade": grade,
                "status": status
            }

        except ValueError as e:
            error = str(e)

    return render_template(
        "marks_calculator.html",
        result=result,
        error=error
    )

@app.route("/invoice-generator")
def invoice_generator():
    return render_template("invoice_generator.html")
if __name__ == "__main__":
    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

