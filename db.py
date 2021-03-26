from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv


app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

def fetchAreaValues():
    result = db.session.execute("""SELECT a.topic, COUNT(t.id), COUNT(m.id) FROM areas a LEFT JOIN threads t
                                 ON a.listed=True AND a.id=t.area_id LEFT JOIN messages m ON m.area_id=a.id GROUP BY a.id ORDER BY a.topic""")
    '''last_post = db.session.execute("""SELECT m.posted_at FROM areas a LEFT JOIN messages m ON a.listed=True
                                 AND m.area_id=a.id GROUP BY m.area_id ORDER BY m.id DESC LIMIT 1""")
    last_post = last_post.fetchall()'''
    areaValues = result.fetchall()

    values = []
    for i in range(len(areaValues)):
        values.append([areaValues[i][0],areaValues[i][1],areaValues[i][2]])#,last_post[i][0]])
    return values

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

