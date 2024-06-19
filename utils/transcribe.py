import os
import requests
from openai import OpenAI
import dotenv
import boto3

dotenv.load_dotenv()
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)


def download_file_from_s3(s3_url, download_path):
    """
    Downloads a file from S3 given the S3 URL.

    :param s3_url: URL of the S3 file
    :param download_path: Local path to save the downloaded file
    :return: Local path of the downloaded file
    """
    bucket_name, key = s3_url.replace("s3://", "").split("/", 1)
    print(f's3_url {s3_url}')

    print("bucket_name")
    print(bucket_name)
    print("key")
    print(key)

    print("download_path")
    print(download_path)
    s3_client.download_file(bucket_name, key, download_path)
    print("downloaded path")

    return download_path


def transcribe_audio_with_whisper(audio_path):
    """
    Transcribes audio using OpenAI's Whisper model.

    :param audio_path: Path to the audio file
    :return: Transcribed text
    """
    client = OpenAI()
    transcript = ""
    with open(audio_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file)
        transcript = response.text

    print(transcript)
    


    return transcript


def transcribe_audio_from_url(audio_url):
    """
    Downloads audio from a URL and transcribes it using OpenAI's Whisper model.

    :param audio_url: S3 URL of the audio file
    :param local_audio_path: Local path to save the downloaded audio file
    :return: Transcribed text
    """
    try:
        # Download the audio file


        
        download_file_from_s3(
            audio_url, 'temp_transcript_audio.mp3')

        # Transcribe the audio file using Whisper
        transcript = transcribe_audio_with_whisper('temp_transcript_audio.mp3')

        # Cleanup: Remove the local audio file
        os.remove('temp_transcript_audio.mp3')

        return transcript
    except Exception as e:
        return str(e)
