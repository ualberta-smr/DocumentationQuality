import os

from urllib.parse import urlparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.11 (KHTML, like Gecko) '
                  'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def make_filename_from_url(library_name, url, ftype):
    parse = urlparse(url)

    filename = parse.path.split("/")[-1]
    if ".htm" in filename:
        filename = filename.rsplit(".", 1)[0]
    filename = filename + "_" + ftype + ".csv"
    return os.path.normpath("results/" + library_name + "/" + filename)

