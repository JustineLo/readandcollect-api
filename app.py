import os
import datetime

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

@app.route('/add_article', methods=['POST'])
def add_article():

    user_uid = request.json.get("uid")
    url = request.json.get("url")
    user_docs = db.collection('users').where('uid', '==', user_uid).get()
    if len(user_docs) == 0:
        return jsonify({'error': 'User not found.'}), 404
    user_doc_id = user_docs[0].id

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

    doc_ref = db.collection('users').document(user_doc_id).collection('articles').document()
    doc_ref.set(new_article)

    # return the response from the create_user endpoint
    return jsonify({
        'title': title,
        'url': url,
        'createdAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'zContent': text
    }), 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))