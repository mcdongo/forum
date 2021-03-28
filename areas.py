from app import app
from db import db

def fetchAreaValues():
    sql = """SELECT a.id, a.topic, COUNT(m.id) FROM areas a LEFT JOIN messages m ON a.listed=True
                                AND m.area_id=a.id AND m.listed=True GROUP BY a.id ORDER BY a.topic"""
    result = db.session.execute(sql).fetchall()
    print(result)

    sql = """SELECT COUNT(t.id) FROM areas a LEFT JOIN threads t ON a.listed=True AND t.area_id=a.id AND t.listed=True GROUP BY a.id
            ORDER BY a.topic"""
    threads = db.session.execute(sql).fetchall()
    print(threads)
    
    sql = """SELECT TO_CHAR(m.posted_at, 'YYYY-MM-DD HH24:MI:SS') AS t FROM messages m, areas a WHERE a.listed=True AND m.listed=True
            ORDER BY t DESC LIMIT 1"""
    last_message = db.session.execute(sql).fetchone()
    areaValues = []
    for i in range(len(result)):
        areaValues.append([result[i][0],result[i][1],result[i][2],threads[i][0]])
    return areaValues,last_message

def getThreads(area_id): #get threads in an area
    sql = "SELECT id, topic, rules FROM areas WHERE id=:id"
    result = db.session.execute(sql,{"id":area_id})
    areaInfo = result.fetchone()

    sql = """SELECT t.id, t.topic, u.username, TO_CHAR(t.posted_at,'YYYY-MM-DD HH24:MI:SS'), u.id FROM threads t, users u WHERE t.op_id=u.id AND t.listed=True and t.area_id=:id
            ORDER BY t.id DESC"""
    result = db.session.execute(sql,{"id":area_id})
    contents = result.fetchall()
    return areaInfo,contents

def createThread(topic,text,area_id,user_id):
    sql = "INSERT INTO threads (topic, message, area_id, posted_at, op_id, listed) VALUES (:topic,:text,:area_id,NOW(),:user_id,True) RETURNING id"
    result = db.session.execute(sql, {"topic":topic,"text":text,"area_id":area_id,"user_id":user_id}).fetchone()[0]
    db.session.commit()
    return result

def checkIfListed(area_id):
    sql = "SELECT listed FROM areas WHERE id=:id"
    result = db.session.execute(sql,{"id":area_id}).fetchone()[0]
    return result

def addArea(topic,rules,listed):
    sql = "INSERT INTO areas (topic, rules, listed) VALUES (:topic, :rules, :listed) RETURNING id"
    result = db.session.execute(sql,{"topic":topic,"rules":rules,"listed":listed}).fetchone()[0]
    db.session.commit()
    return result