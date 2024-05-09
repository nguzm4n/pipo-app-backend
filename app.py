import os
import datetime
from flask import Flask, jsonify, request, json
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv  # Para leer el archivo .env
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Pipo, Comment, Rating

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
jwt = JWTManager(app)
Migrate(app, db)
CORS(app)  # Se evita que se bloqueen las peticiones


@app.route('/token', methods=['GET'])
def token():
    data = {
        "access token": create_access_token(identity="teste@email.com")
    }

    return jsonify(data), 200


@app.route('/pipos', methods=['GET'])
def get_pipos():
    pipos = Pipo.query.all()
    pipos = list(map(lambda pipo: pipo.serialize(), pipos))
    return jsonify(pipos), 200


@app.route('/pipos/<int:id>/detail', methods=['GET'])
def get_pipos_full(id):
    pipo = Pipo.query.get(id)
    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404
    return jsonify(pipo.serialize_with_comment()), 200


@app.route('/pipos', methods=['POST'])
@jwt_required()  # Ruta privada
def add_pipo():
    pipo_info = request.json
    id = get_jwt_identity()

    if not 'pipo_name' in pipo_info:
        return jsonify({"msg": "name is required"}), 400
    elif pipo_info["pipo_name"] == "":
        return jsonify({"msg": "name is required"}), 400
    elif not 'longitude' in pipo_info:
        return jsonify({"msg": "longitude is required"}), 400
    elif pipo_info["longitude"] == "":
        return jsonify({"msg": "longitude is required"}), 400
    elif not 'latitude' in pipo_info:
        return jsonify({"msg": "latitude is required"}), 400
    elif pipo_info["latitude"] == "":
        return jsonify({"msg": "latitude is required"}), 400
    elif not 'address' in pipo_info:
        return jsonify({"msg": "Address is required"}), 400
    elif pipo_info["address"] == "":
        return jsonify({"msg": "Address is required"}), 400

    pipo = Pipo(
        pipo_name=pipo_info["pipo_name"],
        longitude=float(pipo_info["longitude"]),
        latitude=float(pipo_info["latitude"]),
        free=False if not "free" in pipo_info else True,
        disabled=False if not "disabled" in pipo_info else True,
        toiletpaper=False if not "toiletpaper" in pipo_info else True,
        babychanger=False if not "babychanger" in pipo_info else True,
        address=pipo_info["address"],
        user_id=id
    )

    db.session.add(pipo)
    db.session.commit()

    return jsonify({"msg": "Location added succesfully"})


@app.route('/pipos/<int:id>/active', methods=['GET'])
def active_pipo(id):

    pipo = Pipo.query.get(id)
    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404

    pipo.active = True
    db.session.commit()

    return jsonify({"msg": f"Pipo {id} fue activado con éxito"}), 200


@app.route('/pipos/<int:id>/delete', methods=['DELETE'])
@jwt_required()  # Ruta privada
def delete_pipo(id):
    pipo = Pipo.query.get(id)
    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404

    db.session.delete(pipo)
    db.session.commit()

    return jsonify({"msg": f"Pipo con id N°{id} se ha eliminado exitosamente"})

@app.route('/signup', methods=['POST'])
def sign_up():
    print(request.json)
    try:
        user_data = request.json
        if not user_data:
            return jsonify({"msg": "No JSON data received"}), 400

        username = user_data.get('username')
        password = user_data.get('password')
        email = user_data.get('email')
        name = user_data.get('name')
        birthday = user_data.get('birthday', 2000)

        if not username:
            return jsonify({"msg": "username is required"}), 400
        elif username == "":
            return jsonify({"msg": "username is required"}), 400
        elif not password:
            return jsonify({"msg": "password is required"}), 400
        elif password == "":
            return jsonify({"msg": "password is required"}), 400
        elif not email:
            return jsonify({"msg": "email is required"}), 400
        elif email == "":
            return jsonify({"msg": "email is required"}), 400
        elif not name:
            return jsonify({"msg": "name is required"}), 400
        elif name == "":
            return jsonify({"msg": "name is required"}), 400
        elif not birthday:
            return jsonify({"msg": "birthday is required"}), 400

        user_found = User.query.filter_by(email=email).first()
        if user_found:
            return jsonify({"message": "Email is already in use"}), 400

        user_found = User.query.filter_by(username=username).first()
        if user_found:
            return jsonify({"message": "Username is already in use"}), 400

        user = User(
            username=username,
            password=generate_password_hash(password),
            email=email,
            name=name,
            birthday=birthday
        )

        user.save()
        if user:
            expires = datetime.timedelta(hours=72)
            access_token = create_access_token(
                identity=user.id, expires_delta=expires)
            datos = {
                "access_token": access_token,
                "user": user.serialize()

            }
            return jsonify(datos), 201

    except Exception as e:
        return jsonify({"msg": "Error processing JSON data"}), 400


@app.route('/login', methods=["POST"])
def login():

    password = request.json.get('password')
    email = request.json.get('email')
    print(request.json)
    if not password:
        return jsonify({"msg": "password is required"}), 400
    elif password == "":
        return jsonify({"msg": "password is required"}), 400
    elif not email:
        return jsonify({"msg": "email is required"}), 400
    elif email == "":
        return jsonify({"msg": "email is required"}), 400

    user_found = User.query.filter_by(email=email).first()

    if not user_found:
        return jsonify({"message": "email or password is not correct"}), 401

    if not check_password_hash(user_found.password, password):
        return jsonify({"message": "email or password is not correct"}), 401

    expires = datetime.timedelta(hours=72)
    access_token = create_access_token(
        identity=user_found.id, expires_delta=expires)
    datos = {
        "access_token": access_token,
        "user": user_found.serialize()
    }
    return jsonify(datos), 201


@app.route('/pipo/<int:id>/rate', methods=["POST"])
@jwt_required()  # Ruta privada
def add_rating(id):
    pipo = Pipo.query.get(id)
    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404

    rating = request.json
    user_id = get_jwt_identity()

    rate = Rating.query.filter_by(user_id=user_id, pipo_id=pipo.id).first()

    if not rate:

        new_rating = Rating(
            stars=int(rating["stars"]),
            user_id=user_id,
            pipo_id=pipo.id
        )

        db.session.add(new_rating)
        db.session.commit()

    else:
        rate.stars = rating["stars"]
        db.session.commit()

    return jsonify({"msg": "Pipo Succesfully Rated "})


@app.route('/pipo/<int:id>/comment', methods=["POST"])
@jwt_required()  # Ruta privada
def add_comment(id):
    pipo = Pipo.query.get(id)
    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404

    comment = request.json
    user_id = get_jwt_identity()

    comentario = Comment.query.filter_by(
        user_id=user_id, pipo_id=pipo.id).first()

    if not comentario:

        new_comment = Comment(
            comment=comment["comment"],
            user_id=user_id,
            pipo_id=pipo.id,
            date=datetime.datetime.now()

        )

        db.session.add(new_comment)
        db.session.commit()

    else:
        comentario.comment = comment["comment"]
        db.session.commit()

    return jsonify({"msg": "Pipo Succesfully Commented  "})


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
