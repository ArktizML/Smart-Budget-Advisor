from app import create_app
import csv, io
from flask import make_response, session, redirect, flash, url_for, request, render_template
from app.storage import load_data, save_data
from app.users_storage import load_users, save_users
from app.ai import ai
from dotenv import load_dotenv
from groq import Groq
import os

app = create_app()
app.secret_key = "super-secret-key-CHANGE-THIS"
app.register_blueprint(ai)

AVAILABLE_CURRENCIES = [
    "PLN", "EUR", "USD", "GBP", "CHF",
    "SEK", "NOK", "DKK", "CZK"
]


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/download/csv")
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

@app.route("/settings", methods=["GET", "POST"])
def user_settings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    users = load_users()
    user = next((u for u in users if u["id"] == session["user_id"]), None)

    if user is None:
        return redirect(url_for("login"))
    
    if "currency_preference" not in user:
        user["currency_preference"] = "PLN"
        save_users(users)

    if request.method == "POST":
        selected_currency = request.form.get("currency")

        if selected_currency not in AVAILABLE_CURRENCIES:
            flash("Invalid currency selected.", "error")
            return redirect(url_for("user_settings"))
    
        user["currency_preference"] = selected_currency
        save_users(users)
        flash("Settings saved!", "success")

        return redirect(url_for("user_settings"))
    
    return render_template(
        "settings.html",
        user=user,
        currencies=AVAILABLE_CURRENCIES
    )

if __name__ == "__main__":
    app.run(debug=True)