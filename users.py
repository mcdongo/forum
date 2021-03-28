from app import app
from db import db
from routes import session
from werkzeug.security import check_password_hash, generate_password_hash
#everything session and account-related

def login(username,password):
    hash_value = generate_password_hash(password)
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None: #account does not exist
        return 1
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password): #succesful login
            session["username"] = username
            session["user_id"] = getId(username)
            return 3
        else: #wrong password
            return 2 

def logout():
    del session["username"], session["user_id"]

def register(username,password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password,created_at,admin) VALUES (:username,:password,NOW(),False)"
        db.session.execute(sql, {"username":username,"password":hash_value})
        db.session.commit()
        login(username,password)
        return True
    except Exception:
        return False

def getId(username):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    id = result.fetchone()[0]
    return id

def getAdmin(id):
    sql = "SELECT admin FROM users WHERE id=:id"
    result = db.session.execute(sql, {"id":id}).fetchone()[0]
    return result

def checkLoggedInStatus():
    if session["user_id"] != None:
        return True
    return False

def profileData(id):
    sql = "SELECT u.username, TO_CHAR(u.created_at, 'YYYY-MM-DD HH24:MI:SS') FROM users u WHERE id=:id"
    user_info = db.session.execute(sql, {"id":id}).fetchone()

    sql = "SELECT COUNT(m.id) FROM messages m WHERE listed=True AND m.user_id=:id"
    message_count = db.session.execute(sql,{"id":id}).fetchone()[0]
    if message_count == None:
        message_count = 0

    sql = "SELECT COUNT(t.id) FROM threads t WHERE listed=True AND t.op_id=:id"
    thread_count = db.session.execute(sql,{"id":id}).fetchone()[0]
    if thread_count == None:
        thread_count = 0

    stats = [message_count,thread_count]

    sql = """SELECT m.message, t.topic, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS'), a.id, t.id
            FROM messages m, threads t, areas a, users u WHERE u.id=:id AND m.user_id=u.id
            AND m.thread_id=t.id AND m.listed=True AND t.area_id=a.id ORDER BY m.id DESC"""
    message_info = db.session.execute(sql, {"id":id}).fetchall()

    sql = """SELECT t.topic, a.topic, TO_CHAR(t.posted_at, 'YYYY-MM-DD HH24:MI:SS'), a.id, t.id
             FROM threads t, areas a, users u WHERE u.id=:id AND t.op_id=u.id AND a.id=t.area_id AND t.listed=True ORDER BY t.id DESC"""
    thread_info = db.session.execute(sql, {"id":id}).fetchall()

    return user_info,stats,message_info,thread_info

def checkIfExists(id):
    sql = "SELECT username FROM users WHERE id=:id"
    result = db.session.execute(sql,{"id":id}).fetchone()
    if result:
        return True
    return False