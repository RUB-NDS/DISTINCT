import os
import urllib.parse

def dir_path(string):
    if os.path.isdir(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)

def parsed_url(url):
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url
