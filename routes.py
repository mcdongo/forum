from flask import redirect, render_template, request, session, url_for, abort
from app import app
import users, areas, threads

@app.route("/")
def index():
    area_list,last_message,total_messages,total_threads = areas.fetchAreaValues()
    active_threads = areas.getActiveThreads(0)
    if "user_id" in session:
        if users.getAdmin(session["user_id"]):
            return render_template("indexAdmin.html",areas=area_list,last_message=last_message,
                                    threads=active_threads,total_messages=total_messages,total_threads=total_threads)
    session["url"] = url_for("index")
    return render_template("index.html",areas=area_list,last_message=last_message,threads=active_threads,total_messages=total_messages,
                            total_threads=total_threads)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    status = users.login(username,password)
    if status != 3: #unsuccesful login
        return render_template("error.html",message=status)
    if "url" in session: #return to previous page
        return redirect(session["url"])
    return redirect("/") #succesful login

@app.route("/logout")
def logout():
    users.logout()
    if "url" in session:
        return redirect(session["url"]) #return to previous page
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        next_url = "/"
        if "url" in session: 
            next_url = session["url"] #return to previous page 
        return render_template("register.html",next_url=next_url)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.register(username,password):
            if "url" in session:
                return redirect(session["url"]) #return to previous page
            return redirect("/")
        return redirect("/registrationfailed")

@app.route("/registrationfailed")
def registrationFailed():
    next_url = "/"
    if "url" in session:
        next_url = session["url"]
    return render_template("register.html",value="Username already exists.",next_url=next_url)

@app.route("/area/<int:id>")
def area(id):
    if not areas.checkIfListed(id):
        abort(404)
    area, contents = areas.getThreads(id)
    active_threads = areas.getActiveThreads(id)
    session["url"] = url_for("area",id=id)
    return render_template("area.html",area=area,contents=contents,threads=active_threads)

@app.route("/area/<int:area_id>/<int:thread_id>")
def thread(area_id,thread_id):
    if not threads.checkIfListed(thread_id):
        abort(404)
    thread_info,contents = threads.getThreadContent(thread_id)
    session["url"] = url_for("thread",area_id=area_id,thread_id=thread_id)
    return render_template("thread.html",info=thread_info,contents=contents,thread_id=thread_id)

@app.route("/newthread", methods=["POST"])
def newThread():
    if not users.checkLoggedInStatus(): #check if user has logged in -> is allowed to post
        abort(403)
    topic = request.form["topic"]
    message = request.form["message"]
    user_id = session["user_id"]
    area_id = request.form["area_id"]
    if len(topic) > 100 or len(message) > 1000:
        return render_template("error.html",message="Topic or message too long!")

    thread_id = areas.createThread(topic,message,area_id,user_id)

    return redirect("/area/{0}/{1}".format(area_id,thread_id))

@app.route("/reply", methods=["POST"])
def replytoThread():
    if not users.checkLoggedInStatus(): #check if user has logged in -> is allowed to post
        abort(403)
    message = request.form["message"]
    thread_id = request.form["thread_id"]
    area_id = request.form["area_id"]
    user_id = session["user_id"]

    if len(message) > 1000:
        return render_template("error.html",message="Message too long!")
    threads.saveReply(message,thread_id,area_id,user_id)
    return redirect("/area/{0}/{1}".format(area_id,thread_id))

@app.route("/profile/<int:id>")
def profile(id):
    if not users.checkIfExists(id):
        abort(404)
    profile_info, stats, message_info, thread_info = users.profileData(id)
    session["url"] = url_for("profile",id=id)
    return render_template("profile.html",profile=profile_info,stats=stats,messages=message_info,threads=thread_info)

@app.route("/newarea", methods=["POST"])
def newArea():
    if "user_id" in session:
        if users.getAdmin(session["user_id"]):
            topic = request.form["topic"]
            rules = request.form["rules"]
            listed = request.form["listed"]

            areas.addArea(topic,rules,listed)
            return redirect("/")
    else:
        abort(403)

@app.route("/result", methods=["GET"])
def result():
    query = request.args["query"]
    if len(query) < 3:
        return render_template("error.html",message="Search text too short")
    threads,messages,profiles = areas.search(query)
    return render_template("result.html",threads=threads,messages=messages,query=query,profiles=profiles)

@app.route("/editthread/<int:id>", methods=["GET","POST"])
def editThread(id):
    if "user_id" not in session:
        return render_template("error.html", message="You need to log in to edit a thread.")

    if request.method == "GET":
        thread_info, content = threads.getThreadContent(id)
        if threads.checkThreadOwner(id, int(session["user_id"])):
            return render_template("editthread.html",info=thread_info)
        else:
            return render_template("error.html", message="You can't edit someone else's thread!")
    
    if request.method == "POST":
        if "user_id" not in session:
            abort(403)
        message = request.form["message"]
        
        if len(message) > 1000:
            return render_template("error.html", message="Message too long! (over 1000 characters)")
        if threads.editThread(id,int(session["user_id"]),message):
            if "url" in session:
                return redirect(session["url"])
            else:
                return redirect("/")
        else:
            abort(403)

@app.route("/deletethread/<int:area_id>/<int:thread_id>")
def deleteThread(area_id,thread_id):
    if "user_id" not in session:
        return render_template("error.html", message="You need to log in to delete a thread.")
    if threads.deleteThread(thread_id, int(session["user_id"])):
        return redirect("/area/{0}".format(area_id))
    abort(403)

@app.route("/editmessage/<int:id>", methods=["GET","POST"])
def editMessage(id):
    if "user_id" not in session:
        return render_template("error.html", message="You need to log in to edit a message.")
    
    if request.method == "GET":
        message_info = threads.getMessageContent(id)
        if threads.checkMessageOwner(id, int(session["user_id"])):
            return render_template("editmessage.html", info=message_info)
        else:
            return render_template("error.html", message="You can't edit someone else's message!")

    if request.method == "POST":
        message = request.form["message"]
        if len(message) > 1000:
            return render_template("error.html", message="Message too long! (Over 1000 characters)")
        if threads.editMessage(id, int(session["user_id"]), message):
            if "url" in session:
                return redirect(session["url"])
            else:
                return redirect("/")
        else:
            abort(403)


@app.route("/deletemessage/<int:area_id>/<int:thread_id>/<int:message_id>")
def deleteMessage(area_id,thread_id,message_id):
    if "user_id" not in session:
        return render_template("error.html", message="You need to log in to delete a message.")
    if threads.deleteMessage(message_id, int(session["user_id"])):
        return redirect("/area/{0}/{1}".format(area_id, thread_id))
    else:
        abort(403)