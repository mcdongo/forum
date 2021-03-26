from flask import Flask
from flask import redirect, render_template, request, session, url_for
from os import getenv


app = Flask(__name__)
import db
app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    area_list = db.fetchAreaValues()
    return render_template("index.html",areas=area_list)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    status = db.login(username,password)
    if status != 3:
        return redirect(url_for("loginFailed",loginValue=status))
    #succesful login
    session["username"] = username
    return redirect("/")

@app.route("/<int:loginValue>")
def loginFailed(loginValue):
    area_list = db.fetchAreaValues()
    if loginValue == 1: #account does not exist
        message = "Account does not exist!"
    if loginValue == 2: #wrong password
        message = "Wrong password!"
    return render_template("index.html",areas=area_list,loginValue=message)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registration", methods=["POST"])
def registration():
    username = request.form["username"]
    password = request.form["password"]
    if db.register(username,password):
        return redirect("/")
    return redirect("/registrationfailed")

@app.route("/registrationfailed")
def registrationFailed():
    return render_template("register.html",value="Username already exists.")
