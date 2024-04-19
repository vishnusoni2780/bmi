from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class Bmi(db.Model):
    __tablename__ = 'bmi'
    id = db.Column(db.String(),primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(150), unique=True)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    bmi = db.Column(db.Float)

    def __init__(self,name,weight,height,bmi):
        self.name = name
        self.weight = weight
        self.height = height
        self.bmi = bmi
    
