from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database.db import get_db_connection, create_tables
import sqlite3

# FIXED: Flask and Name variables require double underscores
app = Flask(__name__)
app.secret_key = "moneyview_secret"

# Initialize database
create_tables()

# ---------------- AUTH ROUTES ----------------

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )
    user = cursor.fetchone()

    if user:
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        # Check if they already have financial data
        cursor.execute(
            "SELECT 1 FROM financial_data WHERE user_id=? LIMIT 1",
            (user["id"],)
        )
        has_data = cursor.fetchone()
        conn.close()

        if has_data:
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("home"))

    conn.close()
    return render_template("login.html", error="Invalid credentials.")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?,?,?)",
                (name, email, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return "Email already exists."
        finally:
            conn.close()
        return redirect(url_for("login_page"))

    return render_template("register.html")

# ---------------- HOME ----------------

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    
    user_name = session.get("user_name", "Member")
    return render_template("home.html", user_name=user_name)

# ---------------- ONBOARDING ----------------

@app.route("/onboarding/step/<int:step_num>", methods=["GET", "POST"])
def onboarding(step_num):
    if "user_id" not in session:
        return redirect(url_for("login_page"))

    if request.method == "POST":
        # FIXED: Ensure numeric form data is stored as float in the session
        for key, value in request.form.items():
            try:
                session[key] = float(value)
            except (ValueError, TypeError):
                session[key] = value

        if step_num < 5:
            return redirect(url_for("onboarding", step_num=step_num + 1))
        
        return finalize_onboarding()

    templates = {
        1: "step1_income.html",
        2: "step2_expenses.html",
        3: "step3_savings.html",
        4: "step4_debt.html",
        5: "step5_goals.html"
    }
    return render_template(templates.get(step_num, "step1_income.html"))

def finalize_onboarding():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure we get numeric values or default to 0.0
    keys = (
        user_id,
        float(session.get("monthly_income", 0)),
        float(session.get("additional_income", 0)),
        float(session.get("annual_income", 0)),
        float(session.get("bonus_income", 0)),
        float(session.get("housing", 0)),
        float(session.get("food", 0)),
        float(session.get("transportation", 0)),
        float(session.get("utilities", 0)),
        float(session.get("entertainment", 0)),
        float(session.get("other_expenses", 0)),
        float(session.get("current_savings", 0)),
        float(session.get("monthly_savings", 0)),
        float(session.get("stocks_investments", 0)),
        float(session.get("crypto_value", 0)),
        float(session.get("property_value", 0)),
        float(session.get("total_loan", 0)),
        float(session.get("monthly_emi", 0)),
        float(session.get("cc_debt", 0)),
        float(session.get("other_liabilities", 0)),
        float(session.get("savings_goal", 0)),
        session.get("major_purchase", ""),
        session.get("priority", "")
    )

    query = """
    INSERT INTO financial_data (
        user_id, monthly_income, additional_income, annual_income, bonus_income,
        housing, food, transportation, utilities, entertainment, other_expenses,
        current_savings, monthly_savings, stocks_investments, crypto_value,
        property_value, total_loan, monthly_emi, cc_debt, other_liabilities,
        savings_goal, major_purchase, priority
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cursor.execute(query, keys)
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login_page"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    recent_entries = conn.execute(
        "SELECT * FROM financial_data WHERE user_id=? ORDER BY id DESC LIMIT 5",
        (user_id,)
    ).fetchall()
    conn.close()

    if not recent_entries:
        return redirect(url_for("home"))

    data = recent_entries[0]

    # FIXED: Explicitly cast database values to float to prevent math errors
    total_income = float(data["monthly_income"] or 0) + float(data["additional_income"] or 0)
    
    total_expenses = sum([
        float(data["housing"] or 0), float(data["food"] or 0), 
        float(data["transportation"] or 0), float(data["utilities"] or 0), 
        float(data["entertainment"] or 0), float(data["other_expenses"] or 0)
    ])

    total_loan = float(data["total_loan"] or 0)
    current_savings = float(data["current_savings"] or 0)
    
    # Check session goal first, then fallback to db, then default 5000
    savings_goal = float(session.get("savings_goal") or data["savings_goal"] or 5000)

    # Calculation logic for Progress (The fix for the division error)
    progress_percent = min((current_savings / savings_goal) * 100, 100) if savings_goal > 0 else 0

    # ---------- FINANCIAL METRICS ---------- #
    savings_rate = (current_savings / total_income) * 100 if total_income > 0 else 0
    debt_ratio = (total_loan / total_income) * 100 if total_income > 0 else 0
    expense_ratio = (total_expenses / total_income) * 100 if total_income > 0 else 0
    
    health_score = max(0, 100 - (debt_ratio*0.4 + expense_ratio*0.4 - savings_rate*0.2))

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expenses=total_expenses,
        total_loan=total_loan,
        housing=float(data["housing"] or 0),
        food=float(data["food"] or 0),
        transportation=float(data["transportation"] or 0),
        utilities=float(data["utilities"] or 0),
        current_savings=current_savings,
        savings_goal=savings_goal,
        progress_percent=progress_percent,
        health_score=round(health_score),
        debt_ratio=round(debt_ratio, 1),
        savings_rate=round(savings_rate, 1),
        recent_entries=recent_entries,
        user_name=session.get("user_name", "User")
    )

@app.route("/update-profile", methods=["GET","POST"])
def update_profile():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    if request.method == "POST":
        name = request.form.get("name")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET name=%s WHERE id=%s",
            (name, session["user_id"])
        )

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("dashboard.html")

# ---------------- CHATBOT ----------------

@app.route("/chatbot", methods=["GET","POST"])
def chatbot():
    data = request.json
    user_message = data["message"].lower()

    income = session.get("monthly_income", 0)
    expenses = session.get("total_expenses", 0)
    savings = session.get("current_savings", 0)
    debt = session.get("total_loan", 0)

    net = income - expenses

    if "status" in user_message or "condition" in user_message:
        if net > 0:
            condition = "You are financially stable."
        else:
            condition = "Your expenses are higher than your income."

        reply = f"Monthly Income: {income}\nMonthly Expenses: {expenses}\nSavings: {savings}\nDebt: {debt}\n\n{condition}"

    elif "advice" in user_message:
        tips = []
        if expenses > income * 0.7:
            tips.append("Your expenses are high. Reduce unnecessary spending.")
        if savings < income * 0.2:
            tips.append("Try saving at least 20% of your income.")
        if debt > income * 6:
            tips.append("Your debt is high. Focus on debt repayment.")
        if not tips:
            tips.append("Your finances look healthy. Continue saving and investing.")
        reply = "\n".join(tips)

    else:
        reply = "Ask me about your financial condition, expenses, savings, or advice."

    return jsonify({"reply": reply})

# ---------------- UPDATE GOAL ----------------

@app.route("/update-goal", methods=["POST"])
def update_goal():
    if "user_id" in session:
        new_goal = request.form.get("new_goal")
        if new_goal:
            session["savings_goal"] = float(new_goal)
    return redirect(url_for("dashboard"))

# ---------------- OTHER ROUTES ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/settings")
def settings():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("settings.html", user_name=session.get("user_name"))

@app.route("/wisdom")
def wisdom():
    return render_template("wisdom.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)