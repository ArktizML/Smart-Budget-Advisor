from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from .models import Expense, User
from .storage import load_data, save_data
import time, datetime, json, csv, io
from .advisor import analyze_expenses

main = Blueprint('main', __name__)

@main.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    all_expenses = load_data()
    expenses = [e for e in all_expenses if e.get("user_id") == user_id]

    category = request.args.get("category")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    #Category filter
    if category:
        expenses = [e for e in expenses if e['category'].lower() == category.lower()]

    # From-date filter
    if from_date:
        from_dt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        expenses = [e for e in expenses if datetime.datetime.strptime(e["date"], DATE_FORMAT) >= from_dt]

    # To-date filter
    if to_date:
        to_dt = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        expenses = [e for e in expenses if datetime.datetime.strptime(e["date"], DATE_FORMAT) <= to_dt]


    return render_template('index.html', expenses=expenses)

@main.route('/add', methods=['GET', 'POST'])
def add_expense():
    if "user_id" not in session:
        flash("Log in first.", "warning")
        return redirect('/login')
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'].strip())
        except ValueError:
            flash("amount must be a number.")
            return redirect("/add")
        if float(amount) <= 0:
            flash("Amount must be greater than 0.", "error")
            return redirect("/add")
        user_id = session["user_id"]
        category = request.form['category'].strip()
        description = request.form.get('description', '')

        new_expense = Expense(user_id, amount, category, description)
        data = load_data()
        data.append(new_expense.to_dict())
        save_data(data)

        return redirect(url_for('main.index'))
    return render_template('add_expense.html')

@main.route('/delete/<expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    expenses = load_data()

    expenses = [e for e in expenses if not (e["id"] == expense_id and e["user_id"] == user_id)]

    save_data(expenses)
    flash("Expense deleted.", "success")
    return redirect("/")

@main.route('/edit/<expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    data = load_data()
    expense = next((e for e in load_data() if e["id"] == expense_id and e["user_id"] == session["user_id"]), None)
    if expense is None:
        flash("Expense not found.", "error")
        return redirect('/')

    if request.method == "POST":
        new_amount = request.form.get("amount")
        new_category = request.form.get("category")
        new_description = request.form.get("description")

        if not new_amount:
            return redirect(f"/edit/{expense_id}")

        for expense in data:
                if expense['id'] == expense_id:    
                    expense['amount'] = float(new_amount)
                    expense['category'] = new_category or expense.get("category", "")
                    expense['description'] = new_description or expense.get("description", "")
        save_data(data)

        flash("Expense updated!.", "success")
        return redirect('/')

    return render_template('edit_expense.html', expense=expense)

@main.route('/api/expenses', methods=['GET'])
def data_to_json():
    if "user_id" not in session:
        return jsonify([])

    user_id = session["user_id"]
    all_expenses = load_data()
    expenses = [e for e in all_expenses if e.get("user_id") == user_id]
    return jsonify(expenses)

@main.route('/dashboard', methods=["GET", "POST"])
def make_dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template('dashboard.html')

@main.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        password2 = request.form.get("password2")
        # validation
        if password != password2:
            flash("Passwords are incorrect", "danger")
            return redirect("/register")
        user = User.create_user(username, password)
        if user is None:
            flash("User already exists", "danger")
            return redirect("/register")
        #log in
        session["user_id"] = user.id
        session["username"] = user.username
        flash("Registered and logged in", "success")
        return redirect("/")
    return render_template("register.html")


@main.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = User.verify_credentials(username, password)
        if user is None:
            flash("Invaild username or password", "danger")
            return redirect("/login")
        
        session["user_id"] = user.id
        session["username"] = user.username
        flash("Logged in", "success")
        return redirect("/")
    return render_template("login.html")

@main.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect("/")

@main.route('/advisor')
def advisor():
    if "user_id" not in session:
        flash("Log in first.", "warning")
        return redirect("/login")

    user_id = session["user_id"]

    all_expenses = load_data()
    expenses = [e for e in all_expenses if e.get("user_id") == user_id]

    report = analyze_expenses(expenses)

    return render_template("advisor.html", report=report)