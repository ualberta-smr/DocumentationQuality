import os
import html
import re
import traceback
from shutil import rmtree

import mysql.connector

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from git import Repo

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.11 (KHTML, like Gecko) '
                  'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def make_filename_from_url(directory, library_name, url, ftype):
    parse = urlparse(url)

    filename = parse.path.split("/")[-1]
    if ".htm" in filename:
        filename = filename.rsplit(".", 1)[0]
    filename = filename + "_" + ftype + ".csv"
    return os.path.normpath(directory + library_name + "/" + filename)


def get_webpages(doc_home, repo_name):
    req = Request(url=doc_home, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    domain = urlparse(doc_home).hostname
    if not domain:
        print("Invalid Link")

    pages = [doc_home]
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        parse = urlparse(href)
        # hostname is None means it is not an external site
        # path not null means it is another path on the documentation
        # not fragment means it does not have a "#"
        # We do not want links with "#" because they're likely redundant
        if parse.hostname is None:
            if parse.path and not parse.fragment and not parse.query:
                url = re.match(re.compile(".+"), doc_home)[0] + parse.path
                if repo_name.strip().lower() in url.strip().lower():
                    pages.append(url)
        elif parse.hostname == domain and "#" not in href and repo_name.strip().lower() in href.strip().lower():
            pages.append(href)
    pages = list(dict.fromkeys(pages))
    return pages


def add_to_task_table(item_dict):
    website_db = mysql.connector.connect(
        host="localhost",
        user="djangouser",
        password="password",
        database="task_data"
    )
    cursor = website_db.cursor()
    column_names = []
    values = []
    for key, value in item_dict.items():
        column_names.append(key)
        values.append(str(value))
    query = "INSERT INTO overview_task ("
    for column in column_names:
        query += column + ", "
    query = query[:-2] + ") VALUES ("
    for _ in values:
        query += "%s, "
    query = query[:-2] + ");"
    try:
        values = tuple(values)
        cursor.execute(query, values)
        website_db.commit()
        cursor.close()
    except:
        print(traceback.format_exc())
        print(query)


def add_or_update_library_record(item_dict):
    website_db = mysql.connector.connect(
        host="localhost",
        user="djangouser",
        password="password",
        database="task_data"
    )
    cursor = website_db.cursor()
    column_names = []
    values = []
    for key, value in item_dict.items():
        column_names.append(key)
        values.append(str(value))
    query = "SELECT * FROM overview_library WHERE library_name = " + item_dict["library_name"] + ";"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        query = "UPDATE overview_library SET "
        for i in range(len(column_names)):
            query += column_names[i] + " = " + values[i] + ", "
        query = query[:-2] + " WHERE library_name = " + item_dict["library_name"]
    else:
        query = "INSERT INTO overview_library ("
        for column in column_names:
            query += column + ", "
        query = query[:-2] + ") VALUES ("
        for value in values:
            query += value + ", "
        query = query[:-2] + ");"
    cursor.execute(query)
    website_db.commit()
    cursor.close()


def clone_repo(repo_url):
    repo_regex = re.compile(r"(?<=/)[a-zA-Z.-]+(?!/)$")
    repo_name = re.search(repo_regex, repo_url)[0][:-4]
    repo_path = os.path.normpath("MethodLinker/repos/" + repo_name)
    if os.path.exists(repo_path):
        rmtree(repo_path, onerror=rmtree_access_error_handler)
    Repo.clone_from(repo_url, repo_path)
    return repo_path


# Taken from: https://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied
# User: Justin Peel
# At 15:22pm MST
def rmtree_access_error_handler(func, path, exc_info):
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise
