from pymongo import MongoClient
from pymongo import UpdateOne
import datetime
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
campaigns_collection = db['campaigns']


# creates a new campaign in the database
def createCampaign(user_id, name, description, goal, model, videos):
    campaign = {
        'user_id': user_id,
        'name': name,
        'description': description,
        'goal': goal,
        'created': datetime.datetime.now(),
        'script': "",
        'video_url': '',
        'audio_url': "",
        'sync_labs_model': model,
        'sync_labs_model_id': "",
        'eleven_labs_voice_id': "",
        'status': "object_created",
        'sample' : '',
        'videos': videos,
        'clicks': 0

    }

    result = campaigns_collection.insert_one(campaign)
    return str(result.inserted_id)


# gets all campaigns by user_id from the database
def get_campaigns_by_user_id(user_id):
    campaigns = campaigns_collection.find({'user_id': user_id})
    return campaigns


# create a function that takes a map, an id, and updates the campaign with that id with the map
def update_campaign(campaign_data, campaign_id):
    try:
        request = UpdateOne({'_id': ObjectId(campaign_id)}, {'$set': campaign_data})

        result = campaigns_collection.bulk_write([request])


        result = campaigns_collection.find_one({'_id': ObjectId(campaign_id)})



        print("Updated campaign: ", result)



        return True
    except Exception as e:
        print(e)
        return False

    


def get_campaigns_by_status(status):
    campaigns = campaigns_collection.find({'status': status})
    return campaigns


def get_campaigns_by_user_id(user_id):
    campaigns = campaigns_collection.find({'user_id': user_id})
    return json.loads(json_util.dumps(campaigns))


def get_campaign_by_id(campaign_id):
    campaign = campaigns_collection.find_one({'_id': ObjectId(campaign_id)})
    return json.loads(json_util.dumps(campaign))
