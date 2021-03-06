from pathlib import Path
import validators
import datetime

from utils.constants import _TMP_DIR

class FSUtils():
    @staticmethod
    def isTmpDir(path):
        # Return true if this file is anywhere in the tmp dir
        # This will be used to tell the program if it is safe to delete a file
        return Path(path) == Path(_TMP_DIR)


class StrUtils():
    @staticmethod
    def isURL(string):
        return validators.url(string)


    @staticmethod
    def generateFilename(basename='liberty'):
        timestamp = int(datetime.datetime.now().timestamp()*1000)
        return basename+'-'+str(timestamp)