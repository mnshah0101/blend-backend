from werkzeug.utils import secure_filename
import boto3
import os

import dotenv

dotenv.load_dotenv()

# Configure your AWS S3 credentials and bucket name
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Initialize the S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)


def upload_file_to_s3(file, bucket_name, key=None):
    """
    Uploads a file to an S3 bucket.

    :param file: File object to upload
    :param bucket_name: Name of the S3 bucket
    :param s3_client: Boto3 S3 client
    :return: URL of the uploaded file
    """

    print("access")
    print(AWS_ACCESS_KEY_ID)
    print("secret")
    print(AWS_SECRET_ACCESS_KEY)
    print("bucket")
    print(bucket_name)

   
    s3_client.upload_fileobj(file, bucket_name, key)
    # file_uri
    file_url = f"s3://{bucket_name}/{key}"

    return file_url
