from utils.buckets import S3Utils
from utils.constants import _ASSETS_DIR

import os
import logging

logger = logging.getLogger('BucketHandler')

class BucketHandler:
    def __init__(self):
        logger.info('initing Bucket system')
        self.bucket_utils = S3Utils()


    async def download_file(self, dest_path, src_key):
        if not os.path.isdir(os.path.dirname(dest_path)):
            logger.info(f'Directory {os.path.dirname(dest_path)} does not exist, creating it...')
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        self.bucket_utils.download_file(dest_path, src_key)


    async def list_keys(self):
        return self.bucket_utils.list_object_keys()


    async def upload_file(self, path, dest_path):
        return self.bucket_utils.upload_file(path, dest_path)


    async def init_assets(self, keys=None, force=False):
        if keys is None:
            liberty_assets = await self.list_keys()
        else:
            liberty_assets = keys
        for key in liberty_assets:
            dest_path = _ASSETS_DIR + key
            if force or not os.path.exists(dest_path):
                logger.info(f'Downloading asset {key}')
                await self.download_file(dest_path, key)
            else:
                logger.warning(f'Skipping download of {dest_path}, file already exists')
