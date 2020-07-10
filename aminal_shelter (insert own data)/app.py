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
    all_animal_types = client[DB_NAME].animal_types.find()  # 요거는 dropdown을 위한 코딩임

    return render_template('create_animal.template.html',
                           all_animal_types=all_animal_types
                           )


@app.route('/animal/create', methods=['POST'])
def process_create_animal():
    print(request.form)

    animal_name = request.form.get('animal-name')
    animal_type = request.form.get('animal-type')
    animal_breed = request.form.get('breed')

    animal_type_object = client[DB_NAME].animal_types.find_one({  # 요 코딩을 따로 해주는 이유는 Dropdown때문임. dropdown만들고 나서 데이터를 새로insert하면 'type :Dog'이런 식으로 떠야하는데 'type: skdjlskdj' 그 id가 떠버림. 그래서 이 코딩을 통해서 문제를 해결
        "_id": ObjectId(animal_type)                              # btw, mongoDB에 가서 직접 animal_types라는 콜렉션 만들어줬다, 코딩으로 해서 insert한게 아니라. 기억나지? 
    })

    client[DB_NAME].animals.insert_one({  # 'animals'가 colleaction name이 되서 mongoDB Atlas에 collection으로 생성된다.
        "name": animal_name,
        "type": {  # 원래같으면 '"type": Dog'하고 타이핑하면 끝인데 위위에서 말한것처럼 dropdown 만들고나서 제대로 작동안하는 것 때문에 요렇게 해주는거임
            "_id": animal_type_object["_id"],
            "name": animal_type_object["type_name"],
        },
        "breed": animal_breed
    })
    return redirect(url_for('show_all_animals'))


@app.route('/animals')
def show_all_animals():
    all_animals = client[DB_NAME].animals.find().limit(15)  # 이걸 limit(15)으로 걸었더니 데이터를 15개 넘게 넣으니까 페이지에 안보임. 아마 next page버튼 만들어서 넘겨야할 듯

    return render_template('show_animals.template.html',
                           all_animals=all_animals)


@app.route('/animal/update/<id>')
def update_animal(id):
    animal = client[DB_NAME].animals.find_one({
        "_id": ObjectId(id)
    })

    all_animal_types = client[DB_NAME].animal_types.find() #  요것도 dropdown쓰려면 코딩 요렇게 추가해줌

    return render_template('update_animal.template.html',
                           animal=animal,
                           all_animal_types=all_animal_types
                           )


@app.route('/animal/update/<id>', methods=['POST'])
def process_update_animal(id):
    print(request.form)

    animal_name = request.form.get('animal-name')
    animal_type = request.form.get('animal-type')
    animal_breed = request.form.get('breed')

    selected_animal_type = client[DB_NAME].animal_types.find_one({
        "_id": ObjectId(animal_type)
    })

    client[DB_NAME].animals.update_one({
        "_id": ObjectId(id)
    }, {
        "$set": {
            "name": animal_name,
            "type": {
                "_id": selected_animal_type["_id"],
                "name": selected_animal_type["type_name"]
            },
            "breed": animal_breed
        }
    })
    return redirect(url_for('show_all_animals'))


@app.route('/animals/delete/<animal_id>')
def delete_animal(animal_id):
    animal = client[DB_NAME].animals.find_one({
        "_id": ObjectId(animal_id)
    })
    return render_template('confirm_delete.template.html',
                           animal=animal
                           )


@app.route('/animals/delete/<animal_id>', methods=['POST'])
def process_delete_animal(animal_id):
    client[DB_NAME].animals.remove({
        "_id": ObjectId(animal_id),
    })
    return redirect(url_for('show_all_animals'))


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
