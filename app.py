from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "scms-development-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///complaints.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    resolution = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@app.route("/")
def home():
    return "Smart Complaint Management System"

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return "Registration successful!"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_name"] = user.name

            return f"Welcome, {user.name}!"

        return "Invalid email or password."

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return "Logged out successfully!"

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return f"Welcome to your dashboard, {session['user_name']}!"

@app.route("/complaint", methods=["GET", "POST"])
def complaint():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]

        new_complaint = Complaint(
            title=title,
            description=description,
            user_id=session["user_id"]
        )

        db.session.add(new_complaint)
        db.session.commit()

        return "Complaint submitted successfully!"

    return render_template("complaint.html")

@app.route("/complaints")
def complaints():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_complaints = Complaint.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "complaints.html",
        complaints=user_complaints
    )

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)