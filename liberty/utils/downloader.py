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


class PytubeDownloader():
    @staticmethod
    def download(url=None, video=False):
        if not url:
            print("Must Provide URL")
            return None
        # Try to download with pytube, if that fails use yt-dlp
        # TODO: Abstract this into two separate downloader classes and somehow choose between the two (or try them all)
        try:
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
        except:
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
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
            pass
        return YouTubeVideo(title, path, length, video)

