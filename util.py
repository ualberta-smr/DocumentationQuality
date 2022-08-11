import os
import html
import re
import mysql.connector

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import Request, urlopen

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


def make_filename_from_url(library_name, url, ftype):
    parse = urlparse(url)

    filename = parse.path.split("/")[-1]
    if ".htm" in filename:
        filename = filename.rsplit(".", 1)[0]
    filename = filename + "_" + ftype + ".csv"
    return os.path.normpath("results/" + library_name + "/" + filename)


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


def add_or_update_method_record(table, item_dict):
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
    query = "SELECT * FROM " + table + " WHERE library_name = " + item_dict["library_name"] + ";"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        query = "UPDATE " + table + " SET "
        for i in range(len(column_names)):
            query += column_names[i] + " = " + values[i] + ", "
        query = query[:-2] + " WHERE library_name = " + item_dict["library_name"]
    else:
        query = "INSERT INTO " + table + " ("
        for column in column_names:
            query += column + ", "
        query = query[:-2] + ") VALUES ("
        for value in values:
            query += value + ", "
        query = query[:-2] + ");"
    cursor.execute(query)
    website_db.commit()
    cursor.close()
