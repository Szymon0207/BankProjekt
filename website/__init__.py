from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy #zaimportowanie biblotek
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = "1234"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///database.db"
db = SQLAlchemy(app=app)
#przypisanie do bazy danej użytkownika
from website.models import User, Transaction
db.create_all()

login_manager = LoginManager(app=app)
login_manager.login_view = 'login'


def to_float(x):
    try:
        return float(x)
    except:
        return None


def to_int(x):
    try:
        return int(x)
    except:
        return None


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/", methods=["GET"])
@login_required
def home():
    t_out = Transaction.query.filter_by(from_user_id=current_user.id)
    t_in = Transaction.query.filter_by(to_user_id=current_user.id)
    transactions = list(t_in) + list(t_out)
    transactions.sort(key=lambda x: x.date, reverse=True)
    return render_template("home.html", user=current_user, transactions=transactions)


@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transaction():
    if request.method == "POST":
        id = request.form.get("id")
        amount = request.form.get("amount")
        id = to_int(id)
        amount = to_float(amount)

        user = User.query.get(id)
        if not user or user.id == current_user.id:
            flash("Invalid user id!", category="error")
        elif not amount or amount < 0:
            flash("Invalid amount!", category="error")
        elif amount > current_user.balance:
            flash("Amount is bigger than your balance!", category="error")
        else:
            user.balance += amount
            current_user.balance -= amount
            t = Transaction(from_user_id=current_user.id, to_user_id=user.id, amount=amount)
            db.session.add(t)
            db.session.commit()
            flash(f"Sent {amount}zł!", category="success")
            return redirect(url_for("home"))

    return render_template("transaction.html", user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, password=password).first()#zrobienie systemu logowania

        if user:
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Wrong credentials!", "error")

    return render_template("login.html", user=current_user)

#Kod odpowiedzialny za uzytkownikow zalogowanych
@app.route("/signup", methods=["GET", "POST"])#pozwala dziedziczyć po funkcjach flaska
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        user = User.query.filter_by(email=email).first()
#ten kod sprawdza czy hasłą maile i  imię jest dopuszczalnej dlugosci
        if user:
            flash("Account with this emial exists.. ", "error")
        elif len(name) < 3:
            flash("Name is too short.. ", "error")
        elif len(email) < 3:
            flash("Email is too short.. ", "error")
        elif password != password2:
            flash("Passwords are not the same.. ", "error")
        elif len(password) < 3:
            flash("Password is too short.. ", "error")
        else:
            user = User(name=name, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            flash("Account created!", "success")
            return redirect(url_for("login"))

    return render_template("signup.html", user=current_user)

#Kod odpowiadajacy za wylogowanie uzytkownikow ktorzy sa zalogowani
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))