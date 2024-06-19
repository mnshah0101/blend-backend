from pymongo import MongoClient, UpdateOne
import os
import datetime
from bson.objectid import ObjectId
from bson import json_util
import json

# Configure your MongoDB connection
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

# Initialize the MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
videos_collection = db['videos']


# create video object in MongoDB
def create_video(user_id, campaign_id, data, email):
    video = {
        'user_id': user_id,
        'campaign_id': campaign_id,
        'data': data,
        'email': email,
        'script': '',
        'audio_url': '',
        'video_url': '',
        'status': 'object_created',
        'created': datetime.datetime.now(),
        'clicked': False,
        'sync_labs_id': ''
    }

    result = videos_collection.insert_one(video)



    return str(result.inserted_id)


# get all video objects by campaign_id
def get_videos_by_campaign_id(campaign_id):
    videos = videos_collection.find({'campaign_id': campaign_id})
    return videos


# create a function that takes a map, an id, and updates the video with that id with the map
def update_video(video_data, video_id):

    try:

        request = UpdateOne({'_id': ObjectId(video_id)}, {'$set': video_data})

        result = videos_collection.bulk_write([request])

        result = videos_collection.find_one({'_id': ObjectId(video_id)})

        print("Updated video: ", result)
        
        return True
    except Exception as e:
        print(e)
        return False

def get_videos_by_status(status):
    videos = videos_collection.find({'status': status})
    return videos


def get_videos_by_campaign_id(campaign_id):
    videos = videos_collection.find({'campaign_id': campaign_id})
    return json.loads(json_util.dumps(videos))

def get_videos_by_campaign_id_and_status(campaign_id, status):
    videos = videos_collection.find({'campaign_id': campaign_id, 'status': status})
    return videos


def get_videos_by_user_id(user_id):
    videos = videos_collection.find({'user_id': user_id})
    return videos

def get_video_by_id(video_id):
    video = videos_collection.find_one({'_id': ObjectId(video_id)})

    return json.loads(json_util.dumps(video))
