import os
from flask import Flask, jsonify, request, json
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, Pipo, Comment, Rating


load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

db.init_app(app)
Migrate(app, db)
CORS(app)


@app.route('/pipos', methods=['GET'])
def get_pipos():
    pipos = Pipo.query.all()
    pipos = list(map(lambda pipo: pipo.serialize(),pipos))
    return jsonify(pipos), 200


@app.route('/pipos', methods=['POST'])
def add_pipo():
    pipo_info = request.json

    if not 'pipo_name' in pipo_info:
        return jsonify({"msg": "name is required"}), 400
    elif not 'longitude' in pipo_info:
        return jsonify({"msg": "longitude is required"}), 400
    elif not 'latitude' in pipo_info:
        return jsonify({"msg": "latitude is required"}), 400
    elif not 'free' in pipo_info:
        return jsonify({"msg": "Es necesario señalar si el baño es gratuito"}), 400
    if not 'disabled' in pipo_info:
        return jsonify({"msg": "Señalar si es apto para discapacitados"}), 400
    if not 'toiletpaper' in pipo_info:
        return jsonify({"msg": "Señalar si cuenta con papel de baño"}), 400
    if not 'babychanger' in pipo_info:
        return jsonify({"msg": "Señala si hay mudador para bebés"}), 400
    elif pipo_info["longitude"] == "":
        return jsonify({"msg": "longitude is required"}), 400
    elif pipo_info["latitude"] == "":
        return jsonify({"msg": "latitude is required"}), 400
    elif pipo_info["pipo_name"] == "":
        return jsonify({"msg": "name is required"}), 400
    elif pipo_info["free"] is False:
        return jsonify({"msg": "Es necesario señalar si el baño es gratuito"}), 400
    elif pipo_info["disabled"] is False:
        return jsonify({"msg": "Señalar si es apto para discapacitados"}), 400
    elif pipo_info["toiletpaper"] is False:
        return jsonify({"msg": "Señalar si cuenta con papel de baño"}), 400
    elif pipo_info["babychanger"] is False:
        return jsonify({"msg": "Señala si hay mudador para bebés"}), 400


    pipo = Pipo(
        pipo_name=pipo_info["pipo_name"],
        longitude=float(pipo_info["longitude"]),
        latitude=float(pipo_info["latitude"]),
        free=bool(pipo_info["free"]),
        disabled=bool(pipo_info["disabled"]),
        toiletpaper=bool(pipo_info["toiletpaper"]),
        babychanger=bool(pipo_info["babychanger"])
    )

    db.session.add(pipo)
    db.session.commit()

    return jsonify({"msg": "Location added succesfully"})

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()

