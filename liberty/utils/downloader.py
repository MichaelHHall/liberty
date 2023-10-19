import asyncio
from pytube import YouTube
from yt_dlp import YoutubeDL
import json
import time
import logging

from utils.constants import _TMP_DIR
from utils.general import FSUtils, StrUtils

logger = logging.getLogger('DownloaderUtils')

class YouTubeVideo():
    def __init__(self, title, path, length, video):
        self.title = title
        self.path = path
        self.length = length
        self.video = video


class DownloadException(Exception):
    """Exception raised when none of the provided downloaders successfully downloaded"""
    def __init__(self, downloader_list, message="Unable to download video - the url may be bad or the downloaders may be broken"):
        self.downloader_list = downloader_list
        self.message = message
        super().__init__(self.message)


class YouTubeDownloader():
    @staticmethod
    def download(url=None, video=False):
        raise NotImplementedError("No download method implemented for this class")


class PytubeDownloader(YouTubeDownloader):
    @staticmethod
    def download(url=None, dest_dir=_TMP_DIR, video=False):
        if not url:
            logger.warning("Attempting to Download with no URL")
            return None
        yt = YouTube(url)
        if not video:
            streams = yt.streams.filter(only_audio=True)
        else:
            streams = yt.streams.filter(progressive=True)
        # Could filter here to get preferred resolution/file type
        # For more specificity on video/audio would have to move inside the 'if'
        ys = streams.first()
        title = yt.title
        path = ys.download(output_path=dest_dir, filename=StrUtils.generateFilename('youtube'))
        length = yt.length
        return YouTubeVideo(title, path, length, video)


class YoutubeDLDownloader(YouTubeDownloader):
    @staticmethod
    def download(url=None, dest_dir=_TMP_DIR, video=False):
        ts = str(time.time_ns())
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
            'outtmpl': {'default': dest_dir + '%(id)s' + '_' + ts + '.%(ext)s'}
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.sanitize_info(ydl.extract_info(url, download=True))
            title = info.get('title')
            path = dest_dir + info.get('id') + '_' + ts + '.' + info.get('ext')
            length = info.get('duration')
        return YouTubeVideo(title, path, length, video)


ALL_YT_DOWNLOADERS = [YoutubeDLDownloader, PytubeDownloader]

async def download(url=None, dest_dir=_TMP_DIR, video=False, downloaders_list=ALL_YT_DOWNLOADERS):
    """ Attempt to download a video with each given downloader """
    for downloader in downloaders_list:
        try:
            logger.info(f'Attempting to download {url} with {downloader}')
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: downloader.download(url, dest_dir, video))
        except Exception as e:
            logger.error(f'Failed to download with {downloader}')
            logger.error(e)
            continue
    raise DownloadException(downloaders_list)
