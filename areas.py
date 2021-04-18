from app import app
from db import db

def fetchAreaValues():
    sql = """SELECT a.id, a.topic, COUNT(m.id) FROM areas a LEFT JOIN messages m ON
            m.area_id=a.id AND m.listed=True WHERE a.listed=True GROUP BY a.id ORDER BY a.topic"""
    result = db.session.execute(sql).fetchall()

    sql = """SELECT COUNT(t.id) FROM areas a LEFT JOIN threads t ON t.area_id=a.id AND t.listed=True WHERE a.listed=True GROUP BY a.id
            ORDER BY a.topic"""
    threads = db.session.execute(sql).fetchall()
    
    sql = """SELECT TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS') AS t FROM messages m, areas a WHERE a.listed=True AND m.listed=True
            ORDER BY t DESC LIMIT 1"""
    last_message = db.session.execute(sql).fetchone()

    sql = "SELECT COUNT(m.id) FROM messages m WHERE m.listed=True"
    total_messages = db.session.execute(sql).fetchone()

    sql = "SELECT COUNT(t.id) FROM threads t WHERE t.listed=True"
    total_threads = db.session.execute(sql).fetchone()

    areaValues = []
    for i in range(len(result)):
        areaValues.append([result[i][0],result[i][1],result[i][2],threads[i][0]])
    return areaValues,last_message,total_messages,total_threads

def getActiveThreads(area_id=0):
    if area_id == 0:
        sql = """SELECT t.id, t.topic, a.id, a.topic, m.id, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS') as p
                FROM threads t, messages m, areas a WHERE m.thread_id=t.id AND a.id=t.area_id
                AND a.listed=True AND t.listed=True GROUP BY t.id, a.id, m.id ORDER BY m.id DESC LIMIT 10"""
        active_threads = db.session.execute(sql).fetchall()
    else:
        sql ="""SELECT t.id, t.topic, a.id, a.topic, m.id, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS') as p
                FROM threads t, messages m, areas a WHERE m.thread_id=t.id AND a.id=t.area_id
                AND a.listed=True AND t.listed=True AND a.id=:id GROUP BY t.id, a.id, m.id ORDER BY m.id DESC LIMIT 10"""
        active_threads = db.session.execute(sql,{"id":area_id}).fetchall()

    storage = {}
    thread_info = []
    for i in range(len(active_threads)):
        if active_threads[i][0] in storage:
            continue
        storage[active_threads[i][0]]=True
        thread_info.append([active_threads[i][0], active_threads[i][1], active_threads[i][2], active_threads[i][3], active_threads[i][4],
                            active_threads[i][5]])
    return thread_info


def getThreads(area_id): #get threads in an area
    sql = "SELECT id, topic, rules FROM areas WHERE id=:id"
    result = db.session.execute(sql,{"id":area_id})
    areaInfo = result.fetchone()

    sql = """SELECT t.id, t.topic, u.username, TO_CHAR(t.posted_at,'YYYY-MM-DD HH24:MI:SS'), u.id FROM threads t, users u WHERE t.op_id=u.id AND
            t.listed=True and t.area_id=:id ORDER BY t.id DESC"""
    result = db.session.execute(sql,{"id":area_id})
    contents = result.fetchall()
    return areaInfo,contents

def createThread(topic,text,area_id,user_id,img_id=None):
    if img_id:
        sql = """INSERT INTO threads (topic, message, area_id, posted_at, op_id, listed, image_id) VALUES
                (:topic,:text,:area_id, (NOW() + interval '3 hours'),:user_id,True,:image_id) RETURNING id"""
        result = db.session.execute(sql, {"topic":topic,"text":text,"area_id":area_id,"user_id":user_id,"image_id":img_id}).fetchone()[0]
        db.session.commit()
        return result
    sql = "INSERT INTO threads (topic, message, area_id, posted_at, op_id, listed) VALUES (:topic,:text,:area_id,(NOW() + interval '3 hours') ,:user_id,True) RETURNING id"
    result = db.session.execute(sql, {"topic":topic,"text":text,"area_id":area_id,"user_id":user_id}).fetchone()[0]
    db.session.commit()
    return result

def checkIfListed(area_id):
    try:
        sql = "SELECT listed FROM areas WHERE id=:id"
        result = db.session.execute(sql,{"id":area_id}).fetchone()[0]
        return result
    except Exception:
        return None

def addArea(topic,rules,listed):
    sql = "INSERT INTO areas (topic, rules, listed) VALUES (:topic, :rules, :listed) RETURNING id"
    result = db.session.execute(sql,{"topic":topic,"rules":rules,"listed":listed}).fetchone()[0]
    db.session.commit()
    return result

def search(query):
    sql = """SELECT t.area_id, t.id, t.topic, t.message, TO_CHAR(t.posted_at, 'YYYY-MM-DD HH24:MI-SS'), u.username, u.id, a.topic
            FROM threads t, users u, areas a WHERE (t.topic LIKE :query OR t.message LIKE :query OR u.username LIKE :query)
            AND t.op_id=u.id AND t.listed=True AND a.id=t.area_id ORDER BY t.id DESC"""
    threads = db.session.execute(sql,{"query":"%"+query+"%"}).fetchall()

    sql = """SELECT u.id, u.username, t.area_id, t.id, a.topic, m.message, TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS'), t.topic
            FROM users u, threads t, areas a, messages m WHERE (m.message LIKE :query OR u.username LIKE :query)
            AND u.id=m.user_id AND m.thread_id=t.id AND t.area_id=a.id AND t.listed=True AND m.listed=True ORDER BY m.id DESC"""
    messages = db.session.execute(sql,{"query":"%"+query+"%"}).fetchall()

    sql = """SELECT id, username FROM users WHERE username LIKE :query ORDER BY id DESC"""
    profiles = db.session.execute(sql, {"query":"%"+query+"%"}).fetchall()
    return threads, messages, profiles

def areaInfo(area_id):
    sql = "SELECT a.id, a.topic, a.rules FROM areas a WHERE id=:area_id"
    result = db.session.execute(sql, {"area_id":area_id}).fetchone()
    print(result)
    return result

def editArea(topic,rules,listed,id):
    sql = "UPDATE areas SET topic=:topic, rules=:rules, listed=:listed WHERE id=:id"
    result = db.session.execute(sql, {"topic":topic, "rules":rules, "listed":listed, "id":id})
    db.session.commit()
    return
