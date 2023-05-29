from pytube import YouTube
from yt_dlp import YoutubeDL
import json

from utils.constants import _TMP_DIR
from utils.general import FSUtils, StrUtils


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
    def download(url=None, video=False):
        if not url:
            print("Must Provide URL")
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
        path = ys.download(output_path=_TMP_DIR, filename=StrUtils.generateFilename('youtube'))
        length = yt.length
        return YouTubeVideo(title, path, length, video)


class YoutubeDLDownloader(YouTubeDownloader):
    @staticmethod
    def download(url=None, video=False):
        # TODO: Fix known issue where the tmpfile output is not a unique filename, so adding the same video to the queue multiple times causes it to get deleted too early
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
            'outtmpl': {'default': _TMP_DIR + '%(id)s.%(ext)s'}
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.sanitize_info(ydl.extract_info(url, download=True))
            title = info.get('title')
            path = _TMP_DIR + info.get('id') + '.' + info.get('ext')
            length = info.get('duration')
        return YouTubeVideo(title, path, length, video)


ALL_YT_DOWNLOADERS = [YoutubeDLDownloader, PytubeDownloader]

def download(url=None, video=False, downloaders_list=ALL_YT_DOWNLOADERS):
    """ Attempt to download a video with each given downloader """
    for downloader in downloaders_list:
        try:
            return downloader.download(url, video)
        except Exception as e:
            print(e)
            continue
    raise DownloadException(downloaders_list)
