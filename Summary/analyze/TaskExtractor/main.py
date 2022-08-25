import os
from urllib.error import HTTPError

from .extractor import extract_tasks
from .linker import link_tasks
from ..util import get_webpages


def task_extract_and_link(library_name, url, domain):
    pages = get_webpages(url, library_name)
    link_directory = os.path.normpath("TaskExtractor/results/" + library_name)
    if not os.path.exists(link_directory):
        os.mkdir(link_directory)
    # If checking single page, then comment out for loop
    for page in pages:
        try:
            extract_tasks(library_name, page, domain)
            link_tasks(library_name, page)
        except HTTPError:
            pass
    extract_tasks(library_name, url, domain)
    link_tasks(library_name, url)
    if not os.listdir(link_directory):
        os.rmdir(link_directory)
