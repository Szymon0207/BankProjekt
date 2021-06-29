from website import db
from sqlalchemy import func
from flask_login import UserMixin

#utorzenie klasy uzytkownik przechowujace wazne dane
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))
    balance = db.Column(db.Float, default=100)

#utworzenie klasy do transakcji
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer)
    to_user_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime(timezone=True), default=func.now())