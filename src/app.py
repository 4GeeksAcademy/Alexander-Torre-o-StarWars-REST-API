"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():

    # obtiene todos los objetos de usuario de la base de datos
    users = User.query.all()

    # crea una lista de diccionarios con la información de cada usuario
    user_list = [
        {
            "id": user.id,
            "email": user.email
            # agrega aquí cualquier otra información que quieras devolver
        }
        for user in users
    ]

    return jsonify(user_list), 200

@app.route('/planet', methods=['GET'])
def get_planets():
    allPlanets = Planet.query.all()
    result = [element.serialize() for element in allPlanets]
    return jsonify(result), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet1 = Planet.query.get(planet_id)
    if planet1 == None : 
        return 'Planeta no encontrado', 404
    return jsonify(planet1.serialize()), 200

@app.route('/planet', methods=['POST'])
def post_planet():

    # obtain the JSON data from the request and convert it to a Python dictionary
    data = request.get_json()

    # create a new Planet object with the provided data
    planet = Planet(name=data['name'], description=data['description'], population=data['population'])

    # add the new planet to the database
    db.session.add(planet)
    db.session.commit()

    # Serialize the inserted planet data
    inserted_planet_data = planet.serialize()

    return jsonify(inserted_planet_data), 200

@app.route('/people', methods=['GET'])
def get_people():
    allPeople = People.query.all()
    result = [element.serialize() for element in allPeople]
    return jsonify(result),200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_people(people_id):
    people1 = People.query.get(people_id)
    if people1 == None : 
        return 'Persona no encontrada', 404
    return jsonify(people1.serialize()), 200

@app.route('/people', methods=['POST'])
def post_people():

    # obtain the JSON data from the request and convert it to a Python dictionary
    data = request.get_json()

    # create a new People object with the provided data
    people = People(name=data['name'], description=data['description'], gender=data['gender'], hair_color=data['hair_color'])

    # add the new person to the database
    db.session.add(people)
    db.session.commit()

    # Serialize the inserted person data
    inserted_person_data = people.serialize()

    return jsonify(inserted_person_data), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)