import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import yaml
import logging

from utils.constants import _S3_ENDPOINT, _ASSETS_BUCKET_NAME

logger = logging.getLogger('BucketUtils')

class S3Utils():
    def __init__(self):
        # Load S3 secrets
        with open('secrets.yml') as stream:
            try:
                secrets = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)
        self.b2 = boto3.resource(
                service_name='s3',
                endpoint_url=_S3_ENDPOINT,
                aws_access_key_id=secrets['STORAGE_API_ID'],
                aws_secret_access_key=secrets['STORAGE_API_KEY'],
                config=Config(signature_version='s3v4')
        )
        self.b2_client = boto3.client(
                service_name='s3',
                endpoint_url=_S3_ENDPOINT,
                aws_access_key_id=secrets['STORAGE_API_ID'],
                aws_secret_access_key=secrets['STORAGE_API_KEY']
        )


    def download_file(self, file_path, key_name):
        try:
            self.b2.Bucket(_ASSETS_BUCKET_NAME).download_file(key_name, file_path)
        except ClientError as ce:
            logger.error(ce)


    # List the keys of the objects in the assets bucket
    def list_object_keys(self):
        try:
            response = self.b2.Bucket(_ASSETS_BUCKET_NAME).objects.all()

            return_list = []
            for obj in response:
                return_list.append(obj.key)
            return return_list

        except ClientError as ce:
            logger.error(ce)


    def upload_file(self, file_path, b2path=None):
        remote_path = b2path
        if remote_path is None:
            remote_path = file
        try:
            response = self.b2.Bucket(_ASSETS_BUCKET_NAME).upload_file(file_path, remote_path)
        except ClientError as ce:
            logger.error(ce)

        return response
