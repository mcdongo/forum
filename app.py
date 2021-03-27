from flask import Flask
from flask import redirect, render_template, request, session, url_for, abort
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
    session["user_id"] = db.getId(username)
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

@app.route("/area/<int:id>")
def area(id):
    area, contents = db.getArea(id)
    if area == False or contents == False:
        abort(403)
    
    return render_template("area.html",area=area,contents=contents)

@app.route("/area/<int:area_id>/<int:thread_id>")
def thread(area_id,thread_id):
    thread_info,contents = db.getThreadContent(thread_id)
    if thread_info == False: #Check if thread is unlisted=deleted
        abort(403)
    area_name = db.getAreaName(thread_id)
    return render_template("thread.html",info=thread_info,contents=contents,area=[area_id,area_name],thread_id=thread_id)

@app.route("/newthread", methods=["POST"])
def newThread():
    if not session["username"]:
        abort(403)
    topic = request.form["topic"]
    message = request.form["message"]
    user_id = session["user_id"]
    area_id = request.form["area_id"]
    if len(topic) > 100 or len(message) > 1000:
        return redirect("/area/{0}".format(area_id))

    thread_id = db.createThread(topic,message,area_id,user_id)

    return redirect("/area/{0}/{1}".format(area_id,thread_id))

@app.route("/reply", methods=["POST"])
def replytoThread():
    message = request.form["message"]
    thread_id = request.form["thread_id"]
    area_id = request.form["area_id"]
    user_id = session["user_id"]

    if len(message) > 1000:
        return redirect("/area/{0}/{1}".format(area_id,thread_id))

    db.saveReply(message,thread_id,area_id,user_id)
    return redirect("/area/{0}/{1}".format(area_id,thread_id))