import boto3
from moviepy.editor import VideoFileClip
import os
import dotenv

dotenv.load_dotenv()


# Initialize the S3 client
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


def extract_audio_from_video(video_path, audio_output_path):
    """
    Extracts audio from a video file and saves it as an MP3 file.

    :param video_path: Local path to the video file
    :param audio_output_path: Path to save the extracted audio file
    :return: Path to the saved audio file
    """
    print("video_path")
    print(video_path)
    video_clip = VideoFileClip(video_path)
    video_clip.audio.write_audiofile(audio_output_path)
    return audio_output_path


def upload_file_to_s3(file_path, bucket_name, object_name=None):
    """
    Uploads a file to an S3 bucket.

    :param file_path: Path to the file to upload
    :param bucket_name: S3 bucket name
    :param object_name: S3 object name. If not specified, file_name is used
    :return: URL of the uploaded file
    """
    print("hit")
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
  

    if object_name is None:
        object_name = os.path.basename(file_path)
    s3_client.upload_file(file_path, bucket_name, object_name)
    file_url = f"s3://{bucket_name}/{object_name}"
    return file_url


def extract_audio_from_s3_video_and_upload(s3_video_url, local_video_path, local_audio_path, s3_audio_bucket, s3_audio_key):
    """
    Extracts audio from a video stored in S3 and uploads the audio back to S3.

    :param s3_video_url: URL of the video file in S3
    :param local_video_path: Path to save the downloaded video file
    :param local_audio_path: Path to save the extracted audio file
    :param s3_audio_bucket: S3 bucket name to upload the audio file
    :param s3_audio_key: S3 object name for the audio file
    :return: URL of the uploaded audio file
    """
    try:
        # Download the video from S3

        print("s3_video_url")
        download_file_from_s3(s3_video_url, local_video_path)

        # Extract the audio from the video
        print("local_video_path")
        extract_audio_from_video(local_video_path, local_audio_path)

        # Upload the extracted audio back to S3
        print("local_audio_path")
        audio_s3_url = upload_file_to_s3(
            local_audio_path, s3_audio_bucket, s3_audio_key)

        # Cleanup: Remove the downloaded video and audio files
        os.remove(local_video_path)
        os.remove(local_audio_path)

        return audio_s3_url
    except Exception as e:
        return str(e)
