from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentenceDatabase
# create Users collection
users = db['users']

@app.route('/')
def hello():
    return "Hi, there!"

def verify_password(username, password):
    stored_password = users.find({'username': username})[0]['password']
    hashed = bcrypt.hashpw(password.encode('utf8'), stored_password)

    if hashed != stored_password:
        return False
    return True

def get_token(username):
        tokens = users.find({'username': username})[0]['tokens']
        return int(tokens)


class Register(Resource):
    def post(self):
        # get user's posted data
        posted_data = request.get_json()
        username = posted_data['username']
        password = posted_data['password']

        # hash password
        hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(10))

        # store username and password into the database
        users.insert_one({'username': username,
                      'password': hashed,
                      'sentences': '',
                      'tokens': 5})

        return jsonify({'msg': 'Registeration successful!',
                        'status': 200})

class Sentence(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()
        username = posted_data['username']
        password = posted_data['password']
        sentence = posted_data['sentences']

        # if password matched, store sentence
        correct_password = verify_password(username, password)

        if not correct_password:
            return jsonify({'msg': 'Incorrect username or password.',
                            'status': 301})

        token_num = get_token(username)
        if token_num == 0:
            return jsonify({'msg': 'You are out of token, please top up.',
                            'state': 302})

        users.update_one({"username": username}, {"$set":
                                                  {"sentences": sentence,
                                                   "tokens": token_num-1}})
        return {'msg': 'Sentence stores successfully!',
                'status': 200}

class SentenceList(Resource):
    def post(self):
        requested_data = request.get_json()
        username = requested_data['username']
        password = requested_data['password']
        token_num = get_token(username)
        if verify_password(username, password) and token_num > 0:
            users.update_one({"username": username}, {"$set":
                                                          {"tokens": token_num - 1}})
            sentences = users.find({'username': username})[0]['sentences']
            return jsonify({'sentences': sentences,
                            'state': 200})
        return jsonify({'msg': 'You are out of token, please top up.',
                        'state': 302})

class Tokens(Resource):
    def post(self):
        requested_data = request.get_json()
        username = requested_data['username']
        password = requested_data['password']
        token_num = int(requested_data['tokens'])

        if verify_password(username, password):
            tokens = users.find({'username': username})[0]['tokens']
            tokens = int(tokens)
            updated_token = token_num + tokens
            users.update_one({'username': username}, {"$set":{"tokens": updated_token}})
            return jsonify({'msg': f"You current balance is {updated_token} tokens. Thank you for topping up!"})



api.add_resource(Register, '/register')
api.add_resource(Sentence, '/sentence')
api.add_resource(SentenceList, '/sentences')
api.add_resource(Tokens, '/topup')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
