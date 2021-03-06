from flask import Flask, render_template, request, redirect, url_for, flash # 요 flash 해줘야 flashing message사용가능
import os
from dotenv import load_dotenv
from bson import ObjectId  # 요거는 checkbox tick하는 부분 때문에 필요함. bson은 for computer to read json이랑 같은데 컴터 읽기 전용이다.
import pymongo
import datetime  # date사용할 것이므로 요고 써줘야함 

# load in the variable in the .env file into our operating system environment
load_dotenv()

app = Flask(__name__)

# connec to Mongo
MONGO_URI = os.environ.get('MONGO_URL')
client = pymongo.MongoClient(MONGO_URI)

# define my db name
DB_NAME = "todolist"

# read in the SESSION_KEY variable from the operating system environment
SESSION_KEY= os.environ.get('SESSION_KEY')

# set the session key 
app.secret_key = SESSION_KEY

# The HOME route : display all the tasks
@app.route('/')
def home():
    tasks = client[DB_NAME].todos.find().limit(10)
    return render_template('home.template.html',
                           tasks=tasks
                           )


@app.route('/tasks/create')
def show_create_form():
    return render_template('create_task.template.html')


# This is the route that process the form (extract data from it) and write it to the Mongo Database
@app.route('/tasks/create', methods=['POST'])
def create_task():
    print(request.form)

    task_name = request.form.get('task-name')
    due_date = request.form.get('due-date')
    comments = request.form.get('comments')

    client[DB_NAME].todos.insert_one({
        "task_name": task_name,
        "due_date": datetime.datetime.strptime(due_date, "%Y-%m-%d"),
        "comments": comments,
        "done": False
    })
    flash(f"New Task '{task_name}'' has been created")  # 'f' is Formatted String. 요걸 해주면 '{task_name}'이런식으로 string("")안에서도 variable 사용가능
    return redirect(url_for('home'))


# when user tick the checkbox
'''
RESTFUL API Review:
POST - Create new data
PUT - Modify existing data by replacing the old entirely with the new
PATCH - Modify existing data by changing one aspect of the old data 
DELETE - Delete existing data
GET - Fatch data
'''
@app.route('/tasks/check', methods=['PATCH'])
def check_task():
    task_id = request.json.get('task_id')

    task = client[DB_NAME].todos.find_one({
        "_id": ObjectId(task_id)
    })

    # there is a chance that task is not done
    # if there is no key named "done", we just set "done" to False
    if task.get('done') is None:
        task['done'] = False

    client[DB_NAME].todos.update({
        "_id": ObjectId(task_id)
    }, {
        '$set': {
            'done': not task['done']
        }
    })
    # if we return a dictionery in Flask, Flask will auto-convert to JSON. so it is easy to write your own API in Flask!
    # 'home.template.html' 에 써넣은 $.ajx가 성공적으로 통신됐으면 f12 > network> checked 눌러보면 밑의 메세지가 뜰꺼임. 약간 console.log('OK')같은 느낌임 ㅋ
    return {
        "status": "OK"
    }


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)