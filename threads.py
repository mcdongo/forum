from app import app
from db import db
import users


def getThreadContent(thread_id):
    sql = """SELECT t.topic, t.message, u.username, TO_CHAR(t.posted_at, 'YYYY-MM-DD HH24:MI:SS'), u.id, a.id, a.topic FROM threads t, users u, areas a WHERE t.op_id=u.id AND t.id=:thread_id AND t.area_id=a.id"""
    thread_info = db.session.execute(sql,{"thread_id":thread_id}).fetchone()
    
    sql = """SELECT m.message, u.username, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS'), u.id FROM messages m, users u, threads t 
            WHERE m.listed=True AND u.id=m.user_id AND t.id=m.thread_id AND t.id=:thread_id ORDER BY m.id"""
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

def checkIfListed(thread_id):
    sql = "SELECT listed FROM threads WHERE id=:id"
    result = db.session.execute(sql,{"id":thread_id}).fetchone()[0]
    return result