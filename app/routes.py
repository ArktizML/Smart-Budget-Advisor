from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, make_response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from app.currency import get_rates, convert
from .models import Expense, User
from .storage import load_data, save_data
from .users_storage import load_users, save_users, get_current_user
import datetime, csv, io
from .advisor import analyze_expenses

main = Blueprint('main', __name__)

@main.route("/")
def index():
    user = get_current_user()
    if not user:
        return redirect("/login")
    
    user_id = session["user_id"]
    target_currency = user.get("currency", "PLN")
    rates = get_rates()
    all_expenses = load_data()
    expenses = [e for e in all_expenses if e.get("user_id") == user_id]
    for e in expenses:
        original = e["amount"]
        original_currency = e.get("currency", "PLN")
        converted = convert(original, original_currency, target_currency, rates)
        e["converted_amount"] = converted
        e["display_currency"] = target_currency

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


    return render_template('index.html', expenses=expenses, user=user)

@main.route('/add', methods=['GET', 'POST'])
def add_expense():
    if "user_id" not in session:
        flash("Log in first.", "warning")
        return redirect('/login')
    
    users = load_users()
    user = next((u for u in users if u["id"] == session["user_id"]), None)
    categories = user.get("categories", [])

    if request.method == 'POST':
        # user input amount
        try:
            amount_user = float(request.form['amount'].strip())
        except ValueError:
            flash("Amount must be a number.")
            return redirect("/add")

        if amount_user <= 0:
            flash("Amount must be greater than 0.", "error")
            return redirect("/add")

        category = request.form['category']
        description = request.form.get('description', '')[:200]
        user_currency = user.get("currency", "PLN")

        rates = get_rates()

        # --- Convert USER currency → PLN ---
        if user_currency == "PLN":
            amount_pln = amount_user
        else:
            rate = rates.get(user_currency)
            if not rate:
                flash("Unsupported currency.", "error")
                return redirect("/add")

            # user currency → PLN
            amount_pln = round(amount_user / rate, 2)

        # store ONLY PLN
        new_expense = Expense(
            user_id=session["user_id"],
            amount=amount_pln,      # ALWAYS store PLN in DB
            user_currency="PLN",    # stored currency is always PLN
            category=category,
            description=description
        )

        data = load_data()
        data.append(new_expense.to_dict())
        save_data(data)

        return redirect(url_for('main.index'))

    return render_template('add_expense.html', categories=categories)


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
    users = load_users()
    user = next((u for u in users if u["id"] == session["user_id"]), None)
    categories = user.get("categories", [])
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
                    expense['user_currency'] = user.get("currency", "PLN")
        save_data(data)

        flash("Expense updated!.", "success")
        return redirect('/')

    return render_template('edit_expense.html', expense=expense, categories=categories)

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
        default_categories = ["Food", "Transport", "Home", "Entertainment", "Other"]
        # validation
        if password != password2:
            flash("Passwords are incorrect", "danger")
            return redirect("/register")
        user = User.create_user(username, password, default_categories)
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

@main.route('/export_pdf')
def export_pdf():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in.", "danger")
        return redirect("/login")

    # Load users & find username
    users = load_users()
    user = next((u for u in users if u["id"] == user_id), None)
    username = user["username"] if user else "Unknown User"

    # Load expenses
    expenses = load_data()
    user_expenses = [e for e in expenses if e["user_id"] == user_id]

    # -------- ADVISOR SUMMARY --------
    total_spent = sum(e["amount"] for e in user_expenses) if user_expenses else 0
    num_expenses = len(user_expenses)
    biggest = max(user_expenses, key=lambda e: e["amount"]) if user_expenses else None

    # Spending by category
    category_totals = {}
    for e in user_expenses:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    biggest_category = max(category_totals, key=category_totals.get) if category_totals else None

    # Avg daily spending
    if user_expenses:
        dates = [datetime.datetime.strptime(e["date"], "%Y-%m-%d %H:%M:%S") for e in user_expenses]
        days = (max(dates) - min(dates)).days + 1
        avg_daily = round(total_spent / days, 2)
    else:
        avg_daily = 0

    # -------- PDF GENERATION --------
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(40, y, f"Expense Report for {username}")

    y -= 40
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, y, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # -------- SUMMARY SECTION --------
    y -= 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Summary")

    pdf.setFont("Helvetica", 12)
    y -= 20
    pdf.drawString(60, y, f"Total Spending: {total_spent} PLN")

    y -= 20
    pdf.drawString(60, y, f"Number of Expenses: {num_expenses}")

    y -= 20
    pdf.drawString(60, y, f"Average Daily Spending: {avg_daily} PLN")

    y -= 20
    pdf.drawString(60, y, f"Top Category: {biggest_category or 'N/A'}")

    y -= 20
    if biggest:
        pdf.drawString(60, y, f"Biggest Purchase: {biggest['amount']} PLN ({biggest['category']})")
    else:
        pdf.drawString(60, y, "Biggest Purchase: N/A")

    # -------- EXPENSE LIST --------
    y -= 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Expenses")

    pdf.setFont("Helvetica", 10)
    y -= 20

    if not user_expenses:
        pdf.drawString(60, y, "No expenses found.")
    else:
        for e in user_expenses:
            line = f"{e['date']} | {e['category']} | {e['amount']} PLN | {e['description']}"
            pdf.drawString(40, y, line)
            y -= 15

            if y < 40:
                pdf.showPage()
                y = height - 40
                pdf.setFont("Helvetica", 10)

    pdf.save()
    buffer.seek(0)

    filename = f"report_{username}_{datetime.datetime.now().strftime('%Y-%m-%d')}.pdf"

    return send_file(buffer,
                     as_attachment=True,
                     download_name=filename,
                     mimetype="application/pdf")

@main.route("/categories")
def categories():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    users = load_users()

    user = next((u for u in users if u["id"] == user_id), None)

    categories = user.get("categories", ["Food", "Transport", "Rent", "Entertainment", "Other"])

    return render_template("categories.html", categories=categories)

@main.route("/categories/add", methods=["POST"])
def add_category():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    new_cat = request.form.get("category")

    users = load_users()

    user = next((u for u in users if u["id"] == user_id), None)

    if new_cat in user["categories"]:
        flash("Category already exists", "warning")
        return redirect("/categories")

    user["categories"].append(new_cat)

    save_users(users)

    return redirect("/categories")

@main.route("/categories/delete/<cat>", methods=["POST"])
def delete_category(cat):
    user_id = session.get("user_id")

    users = load_users()

    user = next((u for u in users if u["id"] == user_id), None)

    expenses = load_data()

    if any(e["category"] == cat and e["user_id"] == user_id for e in expenses):
        flash("Cannot delete: category has expenses", "danger")
        return redirect("/categories")

    user["categories"].remove(cat)

    save_users(users)

    return redirect("/categories")

@main.route("/health")
def health():
    return {"status": "ok"}, 200

@main.route("/download/csv")
def download_csv():
    if "user_id" not in session:
        flash("Log in first.", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    all_expenses = load_data()

    expenses = [e for e in all_expenses if e.get("user_id") == user_id]

    if not expenses:
        flash("You have no expenses to export.", "warning")
        return redirect("/")

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Date", "Category", "Amount", "Description"])

    for e in expenses:
        writer.writerow([e["id"], e["date"], e["category"], e["amount"], e["description"]])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=expenses.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main.route("/settings", methods=["POST"])
def settings():
    user = get_current_user()
    if not user:
        return redirect("/login")
    
    currency = request.form.get("currency")

    users = load_users()
    for u in users:
        if u["id"] == user["id"]:
            u["currency"] = currency

    save_users(users)

    flash("Settings updated successfully.", "success")


    return redirect("/")
