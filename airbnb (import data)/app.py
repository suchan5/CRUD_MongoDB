from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import pymongo

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URL')
DB_NAME = "sample_airbnb"

client = pymongo.MongoClient(MONGO_URI)

'''
요거는 내 생각에, Mongo Shell로 연결해야만 터미널에서 돌려볼 수 있는듯.

all_accomodations = client[DB_NAME].listingsAndReviews.find().limit(10)
for a in all_accomodations:
    print(a)

'''


@app.route('/')
def show_listings():
    page_number = request.args.get('page')  # get the page number

    if page_number == None:  # if there is no page number(a.k.a None), assume we are at page 0
        page_number = 0
    else:
        page_number = int(page_number)
    print("page_number=", page_number)

    all_listings = client[DB_NAME].listingsAndReviews.find().skip(page_number*20).limit(20)  # skip()요고를 넣어야지만 next 20 listings 버튼을 눌렀을 때 다음 20개로 점프(?)스킵(?)해서 보여준다.
    
    return render_template('show_listings.template.html',
                           all_listings=all_listings,
                           page_number=page_number
                           )


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
