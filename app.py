import os

from flask import Flask, request, jsonify
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials, firestore
import json

from utils import get_html, sanitize, select_content

app = Flask(__name__)
CORS(app)

# Initialize Firestore DB
firebase_credentials = json.loads(os.environ['FIREBASE_CREDENTIALS'])
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

usersdb = db.collection('users').document('nSrEazHXrHfCwwjDPVnD').collection('articles')
articles = usersdb.document('articles')

@app.route("/users", methods=["GET"])
def get_users():
    users = [doc.to_dict() for doc in usersdb.stream()]
    return jsonify(users)


@app.route('/create_user', methods=['POST'])
def create_user():
    # define the new user data
    new_user_data = {
        'displayName': 'John Doe',
        'email': 'john.doe@example.com',
    }

    # add new user to Firestore
    doc_ref = db.collection('users').document()
    doc_ref.set(new_user_data)

    return jsonify({'message': 'User created successfully!'}), 201


@app.route('/add_article', methods=['POST'])
def add_article():

    user_id = 'FDaCwLrkwfu3xxeox1qn'
    url = request.json.get("url")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    }
    html = get_html(url, headers)

    title = ""
    try: 
        if(html.h1):
            title = html.h1.text
        elif(html.title):
            title = html.title.text
        else:
            title = "Untitled"
    except:
        print("title catch error")

    html = sanitize(html.article if html.article else html.body)
    html = select_content(html)
    text = ""
    for tag in html:
        text += str(tag)

    # define the new user data
    new_article = {
        'title': title,
        'url': url,
        'createdAt': firestore.SERVER_TIMESTAMP,
        'zContent': text
    }

    doc_ref = db.collection('users').document(user_id).collection('articles').document()
    doc_ref.set(new_article)

    # return the response from the create_user endpoint
    return jsonify({'message': 'Article added successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
