from datetime import datetime
import uuid
from .storage import load_data
from werkzeug.security import generate_password_hash, check_password_hash
from .users_storage import load_users, save_users

class Expense:
    def __init__(self, amount, category, description=None, date=None):
        self.id = User.id
        self.amount = float(amount)
        self.category = category
        self.description = description or ""
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": str(uuid.uuid4()),
            "user_id": User.id,
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

    
class User:
    def __init__(self, username, password):
        self.id = str(uuid.uuid4()),
        self.username = username,
        self.password = hash(password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password
        }
    
    @staticmethod
    def from_dict(d):
        return User(username=d["username"], password_hash=d["password"], id=d.get("id"))
    
    @staticmethod
    def create_user(username, password):
        users = load_users()  
        for u in users:
            if u["username"].lower() == username.lower():
                return None   

        pw_hash = generate_password_hash(password)  
        user = User(username=username, password_hash=pw_hash)
        users.append(user.to_dict())
        save_users(users)
        return user
    
    @staticmethod
    def find_by_username(username):
        users = load_users()
        for u in users:
            if u["username"].lower() == username.lower():
                return User.from_dict(u)
        return None
    
    def verify_password(self, password):
        return check_password_hash(self.password, password)



    