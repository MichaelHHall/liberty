from pytube import YouTube

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
        yt = YouTube(url)
        if not video:
            streams = yt.streams.filter(only_audio=True)
        else:
            streams = yt.streams.filter(progressive=True)
        # Could filter here to get preferred resolution/file type
        # For more specificity on video/audio would have to move inside the 'if'
        ys = streams.first()
        path = ys.download(output_path=_TMP_DIR, filename=StrUtils.generateFilename('youtube'))
        return YouTubeVideo(yt.title, path, yt.length, video)

