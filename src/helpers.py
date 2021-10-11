import os
import urllib.parse

def file_path(string):
    if os.path.isfile(string):
        return os.path.abspath(string)
    else:
        raise FileNotFoundError(string)

def dir_path(string):
    if os.path.isdir(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)

def parsed_url(url):
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url

def insert_newlines(string, every=100, escape=False):
    lines = str(string).splitlines() # we may get json objects here ...
    newlined = []
    for line in lines:
        for i in range(0, len(line), every):
            newlined.append(line[i:i+every])
    if escape:
        return "\\n".join(newlined)
    else:
        return "\n".join(newlined)
