from flask import Flask, render_template, request, redirect, url_for
import os
from bson.objectid import ObjectId
from dotenv import load_dotenv
import pymongo

load_dotenv()
 
app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URL')
DB_NAME = "animal_shelter"

client = pymongo.MongoClient(MONGO_URI)


@app.route('/')
def home():
    return "Welcome!"


@app.route('/animal/create')
def create_animal():
    return render_template('create_animal.template.html')


@app.route('/animal/create', methods=['POST'])
def process_create_animal():
    print(request.form)

    animal_name = request.form.get('animal-name')
    animal_type = request.form.get('type')
    animal_breed = request.form.get('breed')

    client[DB_NAME].animals.insert_one({  # 'animals'가 colleaction name이 되서 mongoDB Atlas에 collection으로 생성된다.
        "name": animal_name,
        "type": animal_type,
        "breed": animal_breed
    })
    return redirect(url_for('show_all_animals'))


@app.route('/animals')
def show_all_animals():
    all_animals = client[DB_NAME].animals.find().limit(10)
    return render_template('show_animals.template.html',
                           all_animals=all_animals)


@app.route('/animal/update/<id>')
def update_animal(id):
    animal = client[DB_NAME].animals.find_one({
        "_id": ObjectId(id)
    })
    return render_template('update_animal.template.html',
                           animal=animal
                           )


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
