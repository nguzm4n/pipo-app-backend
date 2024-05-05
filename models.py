from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    birthday = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)


class Pipo(db.Model):
    __tablename__ = 'pipos'
    id = db.Column(db.Integer, primary_key=True)
    pipo_name = db.Column(db.String(120))
    address = db.Column(db.String(120))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    active = db.Column(db.Boolean, default=False)
    free = db.Column(db.Boolean)
    disabled = db.Column(db.Boolean)
    toiletpaper = db.Column(db.Boolean)
    babychanger = db.Column(db.Boolean)

    def serialize(self):
        return {
            "id": self.id,
            "pipo_name": self.pipo_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "active": self.active,
            "free": self.free,
            "disabled": self.disabled,
            "toiletpaper": self.toiletpaper,
            "babychanger": self.babychanger
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(120))
    date = db.Column(db.DateTime())
    pipo_id = db.Column(db.Integer, db.ForeignKey('pipos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer)
    pipo_id = db.Column(db.Integer, db.ForeignKey('pipos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
