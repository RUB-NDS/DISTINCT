import os
import urllib.parse
import subprocess

def file_path(string):
    """ Check if file exists and return absolute path """
    if os.path.isfile(string):
        return os.path.abspath(string)
    else:
        raise FileNotFoundError(string)

def dir_path(string):
    """ Check if directory exists and return absolute path """
    if os.path.isdir(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)

def parsed_url(url):
    """ Return parsed URL """
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url

def insert_newlines(string, every=100, escape=False):
    """ Insert newlines after x characters """
    lines = str(string).splitlines() # we may get json objects here ...
    newlined = []
    for line in lines:
        for i in range(0, len(line), every):
            newlined.append(line[i:i+every])
    if escape:
        return "\\n".join(newlined)
    else:
        return "\n".join(newlined)
