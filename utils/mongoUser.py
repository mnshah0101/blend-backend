from pymongo import MongoClient, UpdateOne
from werkzeug.security import generate_password_hash, check_password_hash
import os
from bson.objectid import ObjectId
from bson import json_util
import json


# Configure your MongoDB connection
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

# Initialize the MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db['users']

# creates a new user in the database


def create_user_in_mongo(user_data):
    """
    Inserts a user object into the MongoDB collection.

    :param user_data: Dictionary containing user data
    :return: Inserted user ID
    """
    user = {
        'username': user_data['username'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'password': generate_password_hash(user_data['password']),
        'email': user_data['email']
    }
    result = users_collection.insert_one(user)
    return str(result.inserted_id)


# validates a user's credentials for auth
def validate_user(email, password):
    """
    Validates a user's credentials.

    :param username: Username of the user
    :param password: Password of the user
    :return: User object if credentials are valid, None otherwise
    """
    user = users_collection.find_one({'email': email})

    print("User: ", user)


    if user and check_password_hash(user['password'], password):
        return json.loads(json_util.dumps(user))
    return None


# create a function that takes a map, an id, and updates the user with that id with the map
def update_user(user_data, user_id):
    """
    Updates a user's data in the MongoDB collection.

    :param user_data: Dictionary containing updated user data
    :param user_id: ID of the user to update
    :return: Number of modified documents
    """

    try:
        request = UpdateOne({'_id': ObjectId(user_id)}, {'$set': user_data})
        result = users_collection.bulk_write([request])

        result = users_collection.find_one({'_id': ObjectId(user_id)})

        print("Updated user: ", result)
        
        return True
    except Exception as e:
        print(e)
        return False
    



def user_id_from_email(email):
    """
    Returns the user ID associated with the given email.

    :param email: Email of the user
    :return: User ID
    """
    user = users_collection
    user = user.find_one({'email': email})
    return str(user['_id'])
