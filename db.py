from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv


app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace("://", "ql://",1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

def fetchAreaValues():
    result = db.session.execute("SELECT a.id, a.topic FROM areas a ORDER BY a.topic")
    areaValues = result.fetchall()
    return areaValues

def register(username,password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password,created_at,admin) VALUES (:username,:password,NOW(),False)"
        db.session.execute(sql, {"username":username,"password":hash_value})
        db.session.commit()
        return True
    except Exception:
        return False

def login(username,password):
    hash_value = generate_password_hash(password)
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return 1
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
            return 3
        else:
            return 2

def getArea(id):
    sql = "SELECT listed FROM areas WHERE id=:id"
    result = db.session.execute(sql,{"id":id})
    listed = result.fetchone()
    if not listed[0]:
        return False,False
    sql = "SELECT id, topic, rules FROM areas WHERE id=:id"
    result = db.session.execute(sql,{"id":id})
    areaInfo = result.fetchone()

    sql = "SELECT t.id, t.topic, u.username, t.posted_at FROM threads t, users u WHERE t.op_id=u.id AND t.listed=True and t.area_id=:id"
    result = db.session.execute(sql,{"id":id})
    contents = result.fetchall()
    return areaInfo,contents

def getId(username):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    id = result.fetchone()[0]
    return id

def createThread(topic,text,area_id,user_id):
    sql = "INSERT INTO threads (topic, message, area_id, posted_at, op_id, listed) VALUES (:topic,:text,:area_id,NOW(),:user_id,True) RETURNING id"
    result = db.session.execute(sql, {"topic":topic,"text":text,"area_id":area_id,"user_id":user_id}).fetchone()[0]
    db.session.commit()
    return result

def getThreadContent(thread_id):
    sql = "SELECT listed FROM threads WHERE id=:thread_id"
    result = db.session.execute(sql,{"thread_id":thread_id}).fetchone() #check if thread is unlisted
    if not result:
        return False,False

    sql = "SELECT t.topic, t.message, u.username, t.posted_at FROM threads t, users u WHERE t.op_id=u.id AND t.id=:thread_id"
    thread_info = db.session.execute(sql,{"thread_id":thread_id}).fetchone()
    
    sql = """SELECT m.message, u.username, m.posted_at FROM messages m, users u, threads t WHERE m.listed=True AND u.id=m.user_id
            AND t.id=m.thread_id AND t.id=:thread_id"""
    result = db.session.execute(sql,{"thread_id":thread_id})
    messages = result.fetchall()
    return thread_info,messages

def getAreaName(thread_id):
    sql = "SELECT a.topic FROM areas a, threads t WHERE t.id=:thread_id"
    result = db.session.execute(sql, {"thread_id":thread_id}).fetchone()[0]
    return result

def saveReply(message,thread_id,area_id,user_id):
    sql = "INSERT INTO messages (message,thread_id,area_id,user_id,posted_at,listed) VALUES (:message,:thread_id,:area_id,:user_id,NOW(),True)"
    result = db.session.execute(sql,{"message":message,"thread_id":thread_id,"area_id":area_id,"user_id":user_id})
    db.session.commit()
    return True



