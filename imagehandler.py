from db import db
from PIL import Image
import os

TMP_FOLDER = os.getcwd()+"/tmp/"

def checkImage(file):
    if not file.filename.endswith(".jpg"):
        return "Invalid file type"
    data = file.read()
    if len(data) > 100*5096:
        return "File size too large"
    return True #image acceptable

def fetchImage(file_id):
    sql = "SELECT data FROM images WHERE id=:id AND listed=True"
    result = db.session.execute(sql, {"id":file_id})
    data = result.fetchone()[0]
    return data

def saveImage(data,file):
    if not ((file.filename.endswith(".jpg") or file.filename.endswith(".jpeg")) or file.filename.endswith(".png")):
        return "Invalid file type!"
    file = compressImage(file)
    data = file.read()
    if len(data) > 300*1024: #If too large after compression
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
        
def compressImage(file):
    picture = Image.open(file)
    if file.filename.endswith(".png"): #Conversion from png to jpg
        picture = picture.convert('RGB')

    picture.save("{}tmp.jpg".format(TMP_FOLDER), optimize=True, quality=30)
    file = open("{}tmp.jpg".format(TMP_FOLDER), "rb") #Save temporary file to be saved in database
    os.remove("{}tmp.jpg".format(TMP_FOLDER))
    return file