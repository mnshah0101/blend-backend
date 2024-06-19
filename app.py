from flask import Flask, request, jsonify
import os
import boto3
import re
from flask_cors import CORS, cross_origin
import datetime
import requests
import json

from werkzeug.utils import secure_filename
from utils.s3 import upload_file_to_s3
from utils.llm import create_script
from utils.mongoUser import create_user_in_mongo, validate_user
from utils.mongoCampaign import createCampaign, update_campaign, get_campaigns_by_status, get_campaigns_by_user_id, get_campaign_by_id
from utils.mongoVideo import create_video, update_video, get_videos_by_campaign_id_and_status, get_videos_by_status, get_videos_by_campaign_id, get_video_by_id
from utils.videoProcessing import extract_audio_from_s3_video_and_upload
from utils.transcribe import transcribe_audio_from_url
from utils.elevenLabs import create_voice, create_audio_from_script
from utils.synclabs import create_video_from_audio, get_synclabs_video_from_id
import dotenv

dotenv.load_dotenv()

S3_VIDEO_BUCKET = os.getenv('S3_VIDEO_BUCKET')
S3_AUDIO_BUCKET = os.getenv('S3_AUDIO_BUCKET')
CELERY_URL = os.getenv('CELERY_URL')

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/upload_campaign_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    if 'key' not in request.form:
        return jsonify({'error': 'No key part'}), 400

    file = request.files['file']
    key = request.form['key']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    print(file.filename)

    if file:
        try:
            file_url = upload_file_to_s3(file, S3_VIDEO_BUCKET, 'campaigns/'+ key+'.mp4')
            return jsonify({'file_url': file_url}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File upload failed'}), 400


@app.route('/create_user', methods=['POST'])
def create_user():
    user_data = request.json

    required_fields = ['username', 'first_name',
                       'last_name', 'password', 'email']
    for field in required_fields:
        if field not in user_data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    try:
        user_id = create_user_in_mongo(user_data)
        return jsonify({'user_id': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

   
    
#a route that takes a video file, a json array of csv data, a model, a name, a description, a user_id, and a type
#returns a campaign_id
@app.route('/create_campaign', methods=['POST'])
def create_campaign_endpoint():

    if 'video' not in request.files:
        return jsonify({'error': 'No video file part'}), 400
    if 'data' not in request.form:  
        return jsonify({'error': 'No data part'}), 400
    if 'model' not in request.form:
        return jsonify({'error': 'No model part'}), 400
    if 'name' not in request.form:
        return jsonify({'error': 'No name part'}), 400
    if 'description' not in request.form:
        return jsonify({'error': 'No description part'}), 400
    if 'user_id' not in request.form:
        return jsonify({'error': 'No user_id part'}), 400
    if 'campaign_type' not in request.form:
        return jsonify({'error': 'No campaign_type part'}), 400
    if 'sample' not in request.files:
        return jsonify({'error': 'No sample part'}), 400
    


    video_file = request.files['video']

    sample_file = request.files['sample']


    csv_rows = request.form['data']
    model = request.form['model']
    name = request.form['name']
    description = request.form['description']
    user_id = request.form['user_id']
    campaign_type = request.form['campaign_type']


    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not csv_rows:
        return jsonify({'error': 'No data'}), 400
    
    if not model:
        return jsonify({'error': 'No model'}), 400
    
    if not name:
        return jsonify({'error': 'No name'}), 400
    
    if not description:
        return jsonify({'error': 'No description'}), 400
    
    if not user_id:
        return jsonify({'error': 'No user_id'}), 400
    
    if not campaign_type:
        return jsonify({'error': 'No campaign_type'}), 400

    if not sample_file:
        return jsonify({'error': 'No sample'}), 400
    
    
    campaign_id = None
    csv_rows = json.loads(csv_rows)
    
    try:
        campaign_id = createCampaign(
            user_id, name, description,  campaign_type, model, len(csv_rows))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    print("campaign_id", campaign_id)
    file_url = None

    print('getting video')

    if video_file:

        try:
            file_url = upload_file_to_s3(video_file, S3_VIDEO_BUCKET, 'campaigns/'+ campaign_id+'.mp4')
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    print("got video")

    print(file_url)
        
    
    #update campaign with video url

    try:
        update_campaign({'video_url': file_url}, campaign_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    #now upload the sample file, and update the campaign with the sample file url

    sample_file_url = None

    if sample_file:
            try:
                sample_file_url = upload_file_to_s3(sample_file, S3_AUDIO_BUCKET, 'campaigns/'+ campaign_id+'_sample.mp3')
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            
    
    try:
        update_campaign({'sample': sample_file_url}, campaign_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

    #for each row in the csv, create a video object

    print("running")

    
    video_ids = []
    for row in csv_rows:
        try:
            print("trying")
            print(type(row))
            print(row)
            video_id = create_video(user_id, campaign_id, row, row['Email'])
            video_ids.append(video_id)
        except Exception as e:
            return jsonify({'error': str(e)}), 500



    result, status = process_campaign(campaign_id)
    if status == 500:
        return jsonify({'error': result}), 500

    for video_id in video_ids:
        try:
            requests.post(CELERY_URL + '/process_video',
                          json={'video_id': video_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    
    return jsonify({'campaign_id': campaign_id}), 201


    

    

    
    

        


    


#for every video that has status of video_creating, get the video from the sync labs api and if there is a video_url, update the video with the video_url
@app.route('/get_video_from_sync_labs', methods=['POST'])
def get_video_from_sync_labs_handler():
    videos = get_videos_by_status('video_creating')
    return_videos = []
    for video in videos:
        try:
            response = get_synclabs_video_from_id(video['sync_labs_id'])
            return_videos.append(response)
            print(response)
            if 'url' in response and response['url']:
                update_video({'video_url': response['url']}, str(video['_id']))
                update_video({'status': 'video_created'}, str(video['_id']))

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'success', 'videos': return_videos},), 200


def process_campaign(campaign_id):
    try:
        campaign = get_campaign_by_id(campaign_id)

        if 'status' not in campaign:
            return {'error': 'Campaign does not exist'}, 400

        if campaign['status'] != 'object_created':
            return {'error': 'Campaign is not in object_created status'}, 400

        # Extract audio from video
        audio_s3_url = extract_audio_from_s3_video_and_upload(
            campaign['video_url'], f'campaign_video.mp4', 'campaign_audio.mp3', S3_AUDIO_BUCKET, 'campaigns/' + campaign_id + ".mp3")
        update_campaign({'audio_url': audio_s3_url}, campaign_id)
        update_campaign({'status': 'audio_extracted'}, campaign_id)

        # Transcribe audio
        transcript = transcribe_audio_from_url(audio_s3_url)
        update_campaign({'script': transcript}, campaign_id)
        update_campaign({'status': 'audio_transcribed'}, campaign_id)

        # Create voice
        response = create_voice(campaign['sample'], campaign['name'])
        update_campaign(
            {'eleven_labs_voice_id': response['voice_id']}, campaign_id)
        update_campaign({'status': 'voice_created'}, campaign_id)

        return {'message': 'success'}, 200
    except Exception as e:
        return {'error': str(e)}, 500










#create a function that returns the videos for a campaign
@app.route('/get_videos_for_campaign', methods=['GET'])
def get_videos_for_campaign():
    campaign_id = request.args.get('campaign_id')
    videos = get_videos_by_campaign_id(campaign_id)
    return_videos = []
    for video in videos:
        video['id'] = str(video['_id']['$oid'])
        video['created'] = video['created']['$date']
        return_videos.append(video)
    return jsonify({'videos': return_videos}), 200

#crete a function that returns the campaigns for a user
@app.route('/get_campaigns_for_user', methods=['GET'])
def get_campaigns_for_user():
    user_id = request.args.get('user_id')
    print(user_id)

    campaigns = get_campaigns_by_user_id(user_id)
    return_campaigns = []
    for campaign in campaigns:
        campaign['id'] = str(campaign['_id']['$oid'])
        return_campaigns.append(campaign)
    return jsonify({'campaigns': return_campaigns}), 200

#create a function that takes an email and a password, and returns a user object if the credentials are valid
@app.route('/validate_user', methods=['POST'])
def validate_user_endpoint():
    try:
        user_data = request.json
        required_fields = ['email', 'password']

    

        for field in required_fields:
            if field not in user_data:
                print("missing field")
                return jsonify({'error': f'Missing field: {field}'}), 400
            
        print(user_data['email'])
        print(user_data['password'])

        user = validate_user(user_data['email'], user_data['password'])


        


        if user: 
            user_id = user['_id']['$oid']
            user['id'] = user_id
            return jsonify(user), 200
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    

#get campaign by id
@app.route('/get_campaign_by_id', methods=['GET'])
def get_campaign_by_id_handler():
    try:
        campaign_id = request.args.get('campaign_id')

        campaign = get_campaign_by_id(campaign_id)


        return jsonify(campaign), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
