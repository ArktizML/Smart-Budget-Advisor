from datetime import datetime
import uuid
from .storage import load_data

class Expense:
    def __init__(self, amount, category, description=None, date=None):
        self.amount = float(amount)
        self.category = category
        self.description = description or ""
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": str(uuid.uuid4()),
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date
        }
    
    @staticmethod
    def get_by_id(expense_id):
        expenses = load_data()
        for e in expenses:
            if e['id'] == expense_id:
                return e
        return None
