import os
import requests
import re

from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings, play, save
from utils.videoProcessing import download_file_from_s3
from utils.videoProcessing import upload_file_to_s3
import dotenv

dotenv.load_dotenv()

S3_AUDIO_BUCKET = os.getenv('S3_AUDIO_BUCKET')


ELVENLABS_API_KEY = os.getenv('ELEVEN_LABS_API_KEY')
client = ElevenLabs(
  api_key=ELVENLABS_API_KEY
)

# Create a new voice
def create_voice(s3_uri, voice_name):
    #get s3 file url from uri
    s3_url = s3_uri

    audio = download_file_from_s3(s3_url, "temp.mp3")
    
    
    voice = client.clone(
        name=voice_name,
        description="Joe Rogan Experience Guest", # Optional
        files=[audio],
    )

    os.remove("temp.mp3")

    



    return {"voice_id": voice.voice_id}


def create_audio_from_script(voice_id, script, video_id):


    audio = client.generate(
    text=script,
    voice=Voice(
        voice_id=voice_id,
        settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
    )
    )
    save(audio, "temp_created_audio.mp3")
    print("about to save")
    

    file_url = upload_file_to_s3("temp_created_audio.mp3", S3_AUDIO_BUCKET, f"videos/{video_id}.mp3" )
    os.remove("temp_created_audio.mp3")

    print('removed')
    
    return file_url