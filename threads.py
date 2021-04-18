from app import app
from db import db
import users, imagehandler

def getThreadContent(thread_id):
    sql = """SELECT t.topic, t.message, u.username, TO_CHAR(t.posted_at, 'YYYY-MM-DD HH24:MI:SS'), u.id, a.id, a.topic, t.id, t.image_id
            FROM threads t, users u, areas a WHERE t.op_id=u.id AND t.id=:thread_id AND t.area_id=a.id"""
    thread_info = db.session.execute(sql,{"thread_id":thread_id}).fetchone()
    
    sql = """SELECT m.message, u.username, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS'), u.id, m.id, m.image_id FROM messages m, users u, threads t 
            WHERE m.listed=True AND u.id=m.user_id AND t.id=m.thread_id AND t.id=:thread_id ORDER BY m.id"""
    result = db.session.execute(sql,{"thread_id":thread_id})
    messages = result.fetchall()
    return thread_info,messages

def getAreaName(thread_id):
    sql = "SELECT a.topic FROM areas a, threads t WHERE t.id=:thread_id"
    result = db.session.execute(sql, {"thread_id":thread_id}).fetchone()[0]
    return result

def saveReply(message,thread_id,area_id,user_id,img_id=None):
    if img_id == None:
        sql = """INSERT INTO messages (message,thread_id,area_id,user_id,posted_at,listed,image_id) VALUES
                (:message,:thread_id,:area_id,:user_id, (NOW() + INTERVAL '3 hours') ,True,NULL)"""
        result = db.session.execute(sql,{"message":message,"thread_id":thread_id,"area_id":area_id,"user_id":user_id})
        db.session.commit()
        return True

    sql = """INSERT INTO messages (message,thread_id,area_id,user_id,posted_at,listed,image_id) VALUES
            (:message,:thread_id,:area_id,:user_id, (NOW() + INTERVAL '3 hours') ,True,:image_id)"""
    result = db.session.execute(sql, {"message":message,"thread_id":thread_id,"area_id":area_id,"user_id":user_id,"image_id":img_id})
    db.session.commit()
    return True

def checkIfListed(thread_id):
    try:
        sql = "SELECT listed FROM threads WHERE id=:id"
        result = db.session.execute(sql,{"id":thread_id}).fetchone()[0]
        return result
    except Exception:
        return None

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
    sql = "UPDATE messages SET listed=False WHERE thread_id=:thread_id RETURNING image_id"
    result = db.session.execute(sql,{"thread_id":thread_id})
    if result:
        imagehandler.removeThreadImages(result.fetchall())
    sql = "UPDATE threads SET listed=False WHERE id=:thread_id RETURNING image_id"
    result = db.session.execute(sql,{"thread_id":thread_id})
    db.session.commit()
    if result:
        imagehandler.removeImage(result.fetchone()[0])
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

def messageInflux():
    sql = """SELECT m.id, m.message, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS'), m.image_id, m.area_id, m.thread_id, a.id,
            t.topic, u.username, u.id, a.topic FROM messages m, threads t, users u, areas a WHERE m.listed=True AND t.listed=True
            AND a.listed=True AND m.user_id=u.id AND t.id=m.thread_id AND m.area_id=a.id ORDER BY m.id DESC"""
    result = db.session.execute(sql).fetchall()
    return result
    
def getAllThreads():
    sql = """SELECT t.id, t.topic, t.message, TO_CHAR(t.posted_at, 'YYYY-MM-DD HH24:MI:SS'), t.image_id, t.area_id,
            u.username, u.id, a.topic FROM threads t, users u, areas a WHERE t.listed=True
            AND a.listed=True AND t.op_id=u.id AND t.area_id=a.id ORDER BY t.id DESC"""
    result = db.session.execute(sql).fetchall()
    return result
