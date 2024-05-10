from flask_sqlalchemy import SQLAlchemy
from math import floor
db = SQLAlchemy()


class User(db.Model):
    """
    Tabla correspondiente a los usuarios
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    birthday = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment', backref="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "avatar": self.avatar,
            "email": self.email,
            "birthday": self.birthday,
            "admin": self.admin
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class Pipo(db.Model):
    __tablename__ = 'pipos'
    id = db.Column(db.Integer, primary_key=True)
    pipo_name = db.Column(db.String(120))
    address = db.Column(db.String(300))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    active = db.Column(db.Boolean, default=False)
    free = db.Column(db.Boolean, default=False)
    disabled = db.Column(db.Boolean, default=False)
    toiletpaper = db.Column(db.Boolean, default=False)
    babychanger = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User')
    comments = db.relationship('Comment', backref="pipo")
    ratings = db.relationship('Rating', backref="pipo")


    def serialize(self):
        return {
            "id": self.id,
            "address": self.address,
            "pipo_name": self.pipo_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "active": self.active,
            "free": self.free,
            "disabled": self.disabled,
            "toiletpaper": self.toiletpaper,
            "babychanger": self.babychanger,
            "stars": self.get_rating(),
            "comments":[comment.serialize() for comment in self.comments]

        }

    def serialize_with_comment(self):
        return {
            "id": self.id,
            "address":self.address,
            "pipo_name": self.pipo_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "active": self.active,
            "free": self.free,
            "disabled": self.disabled,
            "toiletpaper": self.toiletpaper,
            "babychanger": self.babychanger,
            "stars": self.get_rating(),
            "comments":[comment.serialize() for comment in self.comments]
            
        }



    def get_rating(self):
        total = len(self.ratings)
        stars = 0
        for rating in self.ratings:
            stars += rating.stars
        return floor(stars/total) if total > 0 else 0



class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(120))
    date = db.Column(db.DateTime())
    pipo_id = db.Column(db.Integer, db.ForeignKey('pipos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def serialize(self):
        return {
            "id":self.id,
            "comments": self.comment,
            "date":self.date,
            "user":self.user.username
        }


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer)
    pipo_id = db.Column(db.Integer, db.ForeignKey('pipos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
