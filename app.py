import os
import datetime
from random import randint
from flask import Flask, jsonify, request, json
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv  # Para leer el archivo .env
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Pipo, Comment, Rating, RecoverPassword

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
        return jsonify({"msg": "Pipo Name is missing!"}), 400
    elif pipo_info["pipo_name"] == "":
        return jsonify({"msg": "Pipo Name is missing!"}), 400
    elif not 'address' in pipo_info:
        return jsonify({"msg": "Pipo Address is missing!"}), 400
    elif pipo_info["address"] == "":
        return jsonify({"msg": "Pipo Address is missing!"}), 400
    elif not 'longitude' in pipo_info:
        return jsonify({"msg": "Longitude is missing!"}), 400
    elif pipo_info["longitude"] == "":
        return jsonify({"msg": "Longitude is missing!"}), 400
    elif not 'latitude' in pipo_info:
        return jsonify({"msg": "Latitude is missing!"}), 400
    elif pipo_info["latitude"] == "":
        return jsonify({"msg": "Latitude is missing!"}), 400

    pipo = Pipo(
        pipo_name=pipo_info["pipo_name"],
        longitude=float(pipo_info["longitude"]),
        latitude=float(pipo_info["latitude"]),
        free=False if not "free" in pipo_info else pipo_info["free"],
        disabled=False if not "disabled" in pipo_info else pipo_info["disabled"],
        toiletpaper=False if not "toiletpaper" in pipo_info else pipo_info["toiletpaper"],
        babychanger=False if not "babychanger" in pipo_info else pipo_info["babychanger"],
        address=pipo_info["address"],
        user_id=id
    )

    db.session.add(pipo)
    db.session.commit()

    return jsonify({"success": "Your PIPO Is Waiting For Review", "pipo": pipo.serialize()})


@app.route('/pipos/<int:id>/active', methods=['GET'])
@jwt_required()
def active_pipo(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    pipo = Pipo.query.get(id)

    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404
    if not user.admin:
        return jsonify({"msg": "You are not allowed to do this"}), 400
    pipo.active = True
    db.session.commit()

    return jsonify({"success": f"Pipo {id} fue activado con éxito"}), 200


@app.route('/pipos/<int:id>/delete', methods=['DELETE'])
@jwt_required()  # Ruta privada
def delete_pipo(id):
    pipo = Pipo.query.get(id)
    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404

    db.session.delete(pipo)
    db.session.commit()

    return jsonify({"success": f"Pipo con id N°{id} se ha eliminado exitosamente"})


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
            return jsonify({"msg": "Email is already in use"}), 400

        user_found = User.query.filter_by(username=username).first()
        if user_found:
            return jsonify({"msg": "Username is already in use"}), 400

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
            return jsonify({"success": "Welcome! Your Registration was Successful", "datos": datos}), 201

    except Exception as e:
        return jsonify({"msg": "Error processing JSON data"}), 400


@app.route('/login', methods=["POST"])
def login():

    password = request.json.get('password')
    email = request.json.get('email')
    print(request.json)
    if not email:
        return jsonify({"msg": "Email is required."}), 400
    if email == "":
        return jsonify({"msg": "Email is required."}), 400
    if not password:
        return jsonify({"msg": "Password is required."}), 400
    elif password == "":
        return jsonify({"msg": "Password is required."}), 400
    

    user_found = User.query.filter_by(email=email).first()

    if not user_found:
        return jsonify({"msg": "Email or password is not correct."}), 401

    if not check_password_hash(user_found.password, password):
        return jsonify({"msg": "Email or password is not correct."}), 401

    expires = datetime.timedelta(hours=72)
    access_token = create_access_token(
        identity=user_found.id, expires_delta=expires)
    datos = {
        "access_token": access_token,
        "user": user_found.serialize()
    }
    return jsonify(datos), 201


@app.route('/changepassword', methods=["POST"])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    data = request.json
    user = User.query.get(current_user_id)

    old_password = data['old_password']
    new_password = data['new_password']
    confirm_password = data['confirm_password']

    if 'old_password' not in data or 'new_password' not in data or 'confirm_password' not in data:
        return jsonify({"msg": "All fields are required"}), 400

    if old_password == "":
        return jsonify({"msg": "All fields are required"}), 400
    if new_password == "":
        return jsonify({"msg": "New password field is missing"}), 400

    if new_password != confirm_password:
        return jsonify({"msg": "New password and confirm password do not match"}), 400

    if new_password == old_password:
        return jsonify({"msg": "New password cannot be the same as the old password"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"success": "Password successfully changed", "data": data}), 200


@app.route('/recover_password', methods=["POST"])
def recover_pass():
    print(request.json)
    email = request.json.get('email')

    num = randint(100000, 999999)
    print(num)

    if not email:
        return jsonify({"msg": "Email is missing."})
    recover = RecoverPassword(
        email=email,
        code=num,  # Set code to num
        active=True
    )
    db.session.add(recover)
    db.session.commit()

    if not recover: return jsonify({"msg": "error al generar codigo"}), 400
    return jsonify(recover.serialize()), 200


@app.route('/reset_password', methods=["POST"])
def reset_password():
    email = request.json.get('email')
    code = request.json.get('code')
    password = request.json.get('password')

    valid = RecoverPassword.query.filter_by(
        email=email, code=code, active=True).first()

    if not email:
        return jsonify({"msg": "Email missing"}), 400
    if not code:
        return jsonify({"msg": "Code missing"}), 400
   
    if not valid:
        return "error"
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return "error"

    # new password
    new_password = generate_password_hash(password)
    user.password = new_password

    db.session.commit()
    if user:
        valid.active=False
        db.session.commit()

    return jsonify({"success": "Password successfully changed"}), 200

    
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

    return jsonify({"success": "Pipo Succesfully Rated "})


@app.route('/pipo/<int:id>/comment', methods=["POST"])
@jwt_required()  # Ruta privada
def add_comment(id):
    pipo = Pipo.query.get(id)
    if not pipo:
        return jsonify({"msg": "Pipo Not Found"}), 404

    comment = request.json
    user_id = get_jwt_identity()

    if "comment" not in comment or not comment["comment"].strip():
        return jsonify({"msg": "Comment cannot be empty"}), 400

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

    return jsonify({"success": "Pipo Succesfully Commented  "})


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
