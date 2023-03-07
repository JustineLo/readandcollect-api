import datetime
import json
import os

import firebase_admin
import requests
from bs4 import BeautifulSoup, Comment
from firebase_admin import credentials, firestore
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Firestore DB
firebase_credentials = json.loads(os.environ['FIREBASE_CREDENTIALS'])
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/add_article', methods=['POST'])
def add_article():

    userDocID = request.json.get("userDocID")
    url = request.json.get("url")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    }
    html = get_html(url, headers)

    title = get_title(html)

    html = sanitize(html.article if html.article else html.body)
    html = select_content(html)

    text = get_text(html)

    # define the new user data
    new_article = {
        'title': title,
        'url': url,
        'createdAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'zContent': text,
        'highlights': []
    }

    doc_ref = db.collection('users').document(userDocID).collection('articles').document()
    doc_ref.set(new_article)

    # return the response from the create_user endpoint
    return jsonify(new_article), 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


def get_html(url, headers):
    request = requests.get(url, headers=headers)
    html = BeautifulSoup(request.content, 'html.parser')
    return html

def get_title(html):
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
    return title

def get_text(html):
    text = ""
    for tag in html:
        text += str(tag)
    return text


def sanitize(soup):
    tag_blacklist = ['script', 'style', 'img',
                     'object', 'embed', 'iframe', 'svg', 'header', 'footer', 'aside', 'button', 'nav', 'audio', 'video', 'input', 'form', 'textarea']

    # Remove HTML comments
    for comment in soup.findAll(
            text=lambda text: isinstance(text, Comment)):
        comment.extract()
    # remove a tags keeping content
    for a in soup.find_all('a', href=True):
        a.replaceWithChildren()
    for img in soup.find_all('img'):
        img.decompose()
    for svg in soup.find_all('svg'):
        svg.decompose()
    # Remove unwanted tags
    for tag in soup.findAll():
        # Remove blacklisted tags and their contents.
        if tag.name in tag_blacklist:
            tag.decompose()
            break

    return soup


def select_content(soup):
    tags_to_keep = ['h1', 'h2', 'h3', 'h4',
                    'h5', 'h6', 'ul', 'ol', 'br']
    tag_array = list()
    for tag in soup.find_all():
        if tag.name == 'pre':
            tag_array.append(tag)
        if tag.name in tags_to_keep:
            sanitize(tag)
            tag_array.append(tag)
        if tag.name == 'p':
            sanitize(tag)
            tag_array.append(tag)
    return tag_array