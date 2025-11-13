from flask import Blueprint, render_template, request, redirect, url_for
from .models import Expense
from .storage import load_data, save_data

main = Blueprint('main', __name__)

@main.route('/')
def index():
    data = load_data()
    return render_template('index.html', expenses=data)

@main.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form.get('description', '')

        new_expense = Expense(amount, category, description)
        data = load_data()
        data.append(new_expense.to_dict())
        save_data(data)

        return redirect(url_for('main.index'))
    return render_template('add_expense.html')