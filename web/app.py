# """
# Registration of a user 0 tokens
# Each user gets 10 tokens
# Store a sentence on our database for 1 token
# Retrieve his stored sentence on out database for 1 token
# """
# from flask import Flask, jsonify, request
# from flask_restful import Api, Resource
# from pymongo import MongoClient
# import bcrypt
#
# app = Flask(__name__)
# api = Api(app)
#
# client = MongoClient("mongodb://db:27017")
# db = client.SentencesDatabase
# users = db["Users"]
#
# class Register(Resource):
#     def post(self):
#         #Step 1 is to get posted data by the user
#         postedData = request.get_json()
#
#         #Get the data
#         username = postedData["username"]
#         password = postedData["password"] #"123xyz"
#
#
#         hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
#
#         #Store username and pw into the database
#         users.insert_one({
#             "Username": username,
#             "Password": hashed_pw,
#             "Sentence": "",
#             "Tokens":6
#         })
#
#         retJson = {
#             "status": 200,
#             "msg": "You successfully signed up for the API"
#         }
#         return jsonify(retJson)
#
# def verifyPw(username, password):
#     hashed_pw = users.find({
#         "Username":username
#     })[0]["Password"]
#
#     if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
#         return True
#     else:
#         return False
#
# def countTokens(username):
#     tokens = users.find({
#         "Username":username
#     })[0]["Tokens"]
#     return tokens
#
# class Store(Resource):
#     def post(self):
#         #Step 1 get the posted data
#         postedData = request.get_json()
#
#         #Step 2 is to read the data
#         username = postedData["username"]
#         password = postedData["password"]
#         sentence = postedData["sentence"]
#
#         #Step 3 verify the username pw match
#         correct_pw = verifyPw(username, password)
#
#         if not correct_pw:
#             retJson = {
#                 "status":302
#             }
#             return jsonify(retJson)
#         #Step 4 Verify user has enough tokens
#         num_tokens = countTokens(username)
#         if num_tokens <= 0:
#             retJson = {
#                 "status": 301
#             }
#             return jsonify(retJson)
#
#         #Step 5 store the sentence, take one token away  and return 200OK
#         users.update_one({
#             "Username":username
#         }, {
#             "$set":{
#                 "Sentence":sentence,
#                 "Tokens":num_tokens-1
#                 }
#         })
#
#         retJson = {
#             "status":200,
#             "msg":"Sentence saved successfully"
#         }
#         return jsonify(retJson)
#
# class Get(Resource):
#     def post(self):
#         postedData = request.get_json()
#
#         username = postedData["username"]
#         password = postedData["password"]
#
#         #Step 3 verify the username pw match
#         correct_pw = verifyPw(username, password)
#         if not correct_pw:
#             retJson = {
#                 "status":302
#             }
#             return jsonify(retJson)
#
#         num_tokens = countTokens(username)
#         if num_tokens <= 0:
#             retJson = {
#                 "status": 301
#             }
#             return jsonify(retJson)
#
#         #MAKE THE USER PAY!
#         users.update_one({
#             "Username":username
#         }, {
#             "$set":{
#                 "Tokens":num_tokens-1
#                 }
#         })
#
#
#
#         sentence = users.find({
#             "Username": username
#         })[0]["Sentence"]
#         retJson = {
#             "status":200,
#             "sentence": str(sentence)
#         }
#
#         return jsonify(retJson)
#
#
#
#
# api.add_resource(Register, '/register')
# api.add_resource(Store, '/store')
# api.add_resource(Get, '/get')
#
#
# if __name__=="__main__":
#     app.run(host='0.0.0.0')

















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
    app.run(host='0.0.0.0', debug=True)