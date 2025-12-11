from app import create_app
import csv, io
from flask import make_response, session, redirect, flash, request
from app.storage import load_data, save_data
from app.users_storage import load_users, save_users, get_current_user
from app.ai import ai
import os
from dotenv import load_dotenv
from groq import Groq

app = create_app()
app.secret_key = "super-secret-key-CHANGE-THIS"
app.register_blueprint(ai)


load_dotenv()
api_key=os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

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

@app.route("/settings", methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=True)