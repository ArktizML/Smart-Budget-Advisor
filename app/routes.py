from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Expense
from .storage import load_data, save_data
import time

main = Blueprint('main', __name__)

@main.route("/")
def index():
    data = load_data()
    return render_template('index.html', expenses=data)

@main.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'].strip())
        except ValueError:
            flash("amount must be a number.")
            return redirect("/add")
        if float(amount) <= 0:
            flash("Amount must be greater than 0.", "error")
            return redirect("/add")
        category = request.form['category'].strip()
        description = request.form.get('description', '')

        new_expense = Expense(amount, category, description)
        data = load_data()
        data.append(new_expense.to_dict())
        save_data(data)

        return redirect(url_for('main.index'))
    return render_template('add_expense.html')

@main.route('/delete/<expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expenses = load_data()

    expenses = [e for e in expenses if e["id"] != expense_id]

    save_data(expenses)
    flash("Expense deleted.", "success")
    return redirect("/")