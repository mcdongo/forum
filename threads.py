from app import app
from db import db
import users


def getThreadContent(thread_id):
    sql = """SELECT t.topic, t.message, u.username, TO_CHAR(t.posted_at, 'YYYY-MM-DD HH24:MI:SS'), u.id, a.id, a.topic, t.id
            FROM threads t, users u, areas a WHERE t.op_id=u.id AND t.id=:thread_id AND t.area_id=a.id"""
    thread_info = db.session.execute(sql,{"thread_id":thread_id}).fetchone()
    
    sql = """SELECT m.message, u.username, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS'), u.id, m.id FROM messages m, users u, threads t 
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

def checkThreadOwner(thread_id,user_id):
    sql = "SELECT op_id FROM threads WHERE id=:thread_id"
    result = db.session.execute(sql, {"thread_id":thread_id}).fetchone()[0]
    return result==user_id

def editThread(thread_id,user_id,message, topic):
    if not (checkThreadOwner(thread_id,user_id) or users.getAdmin(user_id)):
        return False
    sql = "UPDATE threads SET message=:message WHERE id=:thread_id"
    result = db.session.execute(sql, {"message":message,"thread_id":thread_id})
    sql = "UPDATE threads SET topic=:topic WHERE id=:thread_id"
    result = db.session.execute(sql, {"topic":topic,"thread_id":thread_id})
    db.session.commit()
    return True
    
def deleteThread(thread_id,user_id):
    if not (checkThreadOwner(thread_id,user_id) or users.getAdmin(user_id)):
        return False
    sql = "UPDATE messages SET listed=False WHERE thread_id=:thread_id"
    result = db.session.execute(sql,{"thread_id":thread_id})
    sql = "UPDATE threads SET listed=False WHERE id=:thread_id"
    result = db.session.execute(sql,{"thread_id":thread_id})
    db.session.commit()
    return True

def checkMessageOwner(message_id,user_id):
    sql = "SELECT user_id FROM messages WHERE id=:message_id"
    result = db.session.execute(sql,{"message_id":message_id}).fetchone()[0]
    return result==user_id

def getMessageContent(message_id):
    sql = "SELECT message, id FROM messages WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id":message_id}).fetchone()
    return result

def editMessage(message_id,user_id,message):
    if not (checkMessageOwner(message_id,user_id) or users.getAdmin(user_id)):
        return False
    sql = "UPDATE messages SET message=:message WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id":message_id,"message":message})
    db.session.commit()
    return True

def deleteMessage(message_id,user_id):
    if not (checkMessageOwner(message_id,user_id) or users.getAdmin(user_id)):
        return False
    sql = "UPDATE messages SET listed=False WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id":message_id})
    db.session.commit()
    return True

    
