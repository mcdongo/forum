from db import db

def checkImage(file):
    if not file.filename.endswith(".jpg"):
        return "Invalid file type"
    data = file.read()
    if len(data) > 100*2048:
        return "File size too large"
    return True #image acceptable

def fetchImage(file_id):
    sql = "SELECT data FROM images WHERE id=:id AND listed=True"
    result = db.session.execute(sql, {"id":file_id})
    data = result.fetchone()[0]
    return data

def saveImage(data,file):
    if not file.filename.endswith(".jpg"):
        return "Invalid file type"
    #data = file.read()
    if len(data) > 100*2048:
        return "File size too large"
    sql = "INSERT INTO images (data, listed) VALUES (:data, True) RETURNING id"
    Id = db.session.execute(sql, {"data":data}).fetchone()[0]
    db.session.commit()
    return Id

def checkIfListed(img_id):
    sql = "SELECT listed FROM images WHERE id=:id"
    result = db.session.execute(sql, {"id":img_id}).fetchone()[0]
    return result

def removeImage(img_id):
    sql = "UPDATE images SET listed=False WHERE id=:img_id"
    result = db.session.execute(sql, {"img_id":img_id})
    db.session.commit()
    return True

def removeThreadImages(id_list):
    for id in id_list:
        removeImage(id[0])
    return
        