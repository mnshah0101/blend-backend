import os 
import dotenv
import requests


dotenv.load_dotenv()

sync_labs_api_key=os.getenv('SYNC_LABS_API_KEY')

url = "https://api.synclabs.so/lipsync"




def create_video_from_audio(audio_url, video_url):
    headers = {
    "x-api-key": sync_labs_api_key,
    }

    print("api key")
    print(sync_labs_api_key)


    if 's3://' in audio_url:
        bucket = audio_url.split('/')[2]
        key = '/'.join(audio_url.split('/')[3:])
        audio_url = f"https://{bucket}.s3.amazonaws.com/{key}"

    if 's3://' in video_url:
        bucket = video_url.split('/')[2]
        key = '/'.join(video_url.split('/')[3:])
        video_url = f"https://{bucket}.s3.amazonaws.com/{key}"



    

    data = {
    "audioUrl": audio_url,
    "videoUrl": video_url
    }

    print(data)

    response = requests.post(url, data=data, headers=headers)

    print("response")

    print(response.json())


    response = response.json()




    return response


def get_synclabs_video_from_id(video_id):
    headers = {
    "x-api-key": sync_labs_api_key,
    }

    url = f"https://api.synclabs.so/lipsync/{video_id}"

   


    response = requests.get(url, headers=headers)

    return response.json()
        