import csv
import os
import html
import re
import traceback
from collections import deque
from multiprocessing.pool import ThreadPool
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

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "djangouser",
    "password": "password",
    "database": "task_data"
}


def make_filename_from_url(directory, library_name, url, ftype):
    parse = urlparse(url)

    filename = parse.path.split("/")[-1]
    if ".htm" in filename:
        filename = filename.rsplit(".", 1)[0]
    if filename == "":
        filename = library_name
    filename = filename + "_" + ftype + ".csv"
    return os.path.normpath(directory + library_name + "/" + filename)


def get_webpages(doc_home, repo_name):
    req = Request(url=doc_home, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    domain = urlparse(doc_home).hostname
    if not domain:
        print("Invalid Link")

    base_url = re.match(re.compile(".+\/"), doc_home)[0]
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
                url = base_url + parse.path
                if repo_name.strip().lower() in url.strip().lower():
                    pages.append(url)
        elif parse.hostname == domain and "#" not in href and repo_name.strip().lower() in href.strip().lower():
            pages.append(href)
    pages = list(dict.fromkeys(pages))
    return pages


def fetch_url(page_data):
    url = page_data[0]
    depth = page_data[1]
    try:
        req = Request(url=url, headers=HEADERS)
        response = urlopen(req)
    except:
        return None
    return response, depth


def get_all_webpages(doc_home, max_depth):
    print("Getting pages up-to depth", max_depth)
    pages = {}
    stop_words = ['releasenotes', 'whatsnew', 'deprecated', 'community', 'updates', 'releasehistory', 'release-history']

    dq = deque([[doc_home, 0]])

    request_batch = []
    batch_size = 100
    visited_links = set()
    while dq:
        page, depth = dq.popleft()
        # print("Popped ----->  " + page)
        # print("Depth ----->  " + str(depth))

        if any(stop_word in page for stop_word in stop_words):
            continue

        request_batch.append([page, depth])
        if len(request_batch) < batch_size and dq:
            continue
        valid_requests = []
        for data in request_batch:
            page, depth = data[0], data[1]
            if depth <= max_depth:
                valid_requests.append((page, depth))
        if not valid_requests:
            continue
        responses = ThreadPool(min(batch_size, len(valid_requests))).imap_unordered(fetch_url, valid_requests)
        for response_data in responses:
            if response_data is None:
                continue
            response = response_data[0]
            depth = response_data[1]

            try:
                page_url = response.url
                content = html.unescape(response.read().decode("utf-8"))
                soup = BeautifulSoup(content, "html.parser")
                domain = urlparse(page_url).hostname
                if not domain:
                    print("Invalid Link")
                    continue

                pages[page_url] = soup

                base_url = re.match(re.compile(".+\/"), page_url)[0]

                links = set(soup.find_all("a", href=True))
                links = [x for x in links if x not in visited_links]
                visited_links.update(links)

                for link in links:
                    href = link["href"]

                    # Redirecting to parent
                    if re.findall('.*\.\.\/.*', href):
                        continue

                    # Remove one or more './' from link
                    href = re.sub('(\.\/)*', '', href)

                    parse = urlparse(href)
                    # hostname is None means it is not an external site
                    # path not null means it is another path on the documentation
                    # not fragment means it does not have a "#"
                    # We do not want links with "#" because they're likely redundant
                    if parse.hostname is None:
                        if parse.path and not parse.fragment and not parse.query:
                            url = base_url + parse.path
                            if url not in dq and url not in pages and urlparse(url).hostname == urlparse(
                                    doc_home).hostname:
                                # print(url)
                                dq.append([url, depth + 1])
                    elif href not in dq and href not in pages and parse.hostname == domain and "#" not in href and urlparse(
                            href).hostname == urlparse(doc_home).hostname:
                        # print(href)
                        dq.append([href, depth + 1])
            except Exception as e:
                pass
        request_batch.clear()

    return pages


def add_to_task_table(item_dict):
    website_db = mysql.connector.connect(**MYSQL_CONFIG)
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
    website_db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = website_db.cursor()
    column_names = []
    values = []
    for key, value in item_dict.items():
        column_names.append(key)
        values.append(value)
    query = "SELECT * FROM overview_library WHERE library_name = '" + str(item_dict["library_name"]) + "';"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        query = "UPDATE overview_library SET "
        for i in range(len(column_names)):
            query += column_names[i] + " = %s, "
        query = query[:-2] + " WHERE library_name = '" + item_dict["library_name"] + "'"
    else:
        query = "INSERT INTO overview_library ("
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


def clone_repo(repo_url, clone):
    repo_regex = re.compile(r"(?<=/)[a-zA-Z.-]+(?!/)$")
    try:
        repo_name = re.search(repo_regex, repo_url)[0]
        if repo_name[-4:] == ".git":
            repo_name = repo_name[:-4]
        else:
            repo_url = repo_url + ".git"
        repo_path = os.path.normpath("MethodLinker/repos/" + repo_name)
        if clone:
            if os.path.exists(repo_path):
                rmtree(repo_path, onerror=rmtree_access_error_handler)
            Repo.clone_from(repo_url, repo_path)
    except Exception as e:
        repo_path = None
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


def _find_raw_task_csvs(library_name):
    file_dict = dict()
    root = os.path.normpath(ROOT_DIR + "/TaskExtractor/results/" + library_name)
    for file in os.listdir(root):
        # NOTE: This can be hardcoded because we know 100% what the data is
        # Otherwise this is very bad practice. However, we know we need to
        # remove the "_tasks.csv" or "_links.csv" with 100% certainty
        name = file[:-10]
        if name not in file_dict:
            if file.endswith("_tasks.csv"):
                file_dict[name] = {
                    "task_file": os.path.normpath(root + "/" + file)}
            else:
                file_dict[name] = {
                    "link_file": os.path.normpath(root + "/" + file)}
        else:
            if file.endswith("_tasks.csv"):
                file_dict[name]["task_file"] = os.path.normpath(
                    root + "/" + file)
            else:
                file_dict[name]["link_file"] = os.path.normpath(
                    root + "/" + file)
    return file_dict


def _process(library_name, datafiles):
    file_dict = {}
    for key, value in datafiles.items():
        task_list, link_list = None, None
        if "task_file" in value:
            task_file = open(value["task_file"], "r", encoding="utf-8",
                             newline="")
            task_reader = csv.reader(task_file)
            next(task_reader, None)
            task_list = list(task_reader)
            task_file.close()
        if "link_file" in value:
            link_file = open(value["link_file"], "r", encoding="utf-8",
                             newline="")
            link_reader = csv.reader(link_file)
            next(link_reader, None)
            link_list = list(link_reader)
            link_file.close()

        if task_list:
            for row in task_list:
                paragraph = row[0]
                tasks = row[1].split("\n")
                tasks = list(filter(None, [task.strip() for task in tasks]))
                if paragraph not in file_dict:
                    file_dict[paragraph] = {"tasks": tasks}

        if link_list:
            for row in link_list:
                paragraph = row[0]
                if paragraph in file_dict:
                    file_dict[paragraph]["has_example"] = True
                    file_dict[paragraph]["example_page"] = row[3]
                    file_dict[paragraph]["html_id"] = row[2]

    processed_directory = ROOT_DIR + "/TaskExtractor/processed/" + library_name
    if not os.path.exists(processed_directory):
        os.mkdir(processed_directory)
    processed_file_name = os.path.normpath(processed_directory + "/" + key + ".csv")
    with open(processed_file_name, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["library_name", "paragraph", "task", "has_example", "example_page",
             "html_id"])
        for key, value in file_dict.items():
            for task in value["tasks"]:
                writer.writerow([library_name,
                                 key,
                                 task,
                                 1 if "has_example" in value else 0,
                                 value["example_page"] if "example_page" in value else "",
                                 value["html_id"] if "html_id" in value else ""
                                 ])
    # shutil.copy(processed_file_name, os.path.normpath("\\".join(ROOT_DIR.split("\\")[:-1]) + "/Summary/overview/data/processed"))
    return processed_file_name


def _get_library_id(library_name):
    mydb = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id FROM overview_library WHERE library_name = '" + library_name + "'")
    library_id = cursor.fetchone()["id"]
    cursor.close()
    return library_id


def add_tasks_to_db(library_name):
    files = _find_raw_task_csvs(library_name)
    file_name = _process(library_name, files)
    # library_id = _get_library_id(library_name)
    with open(file_name, "r", encoding="utf-8", newline="") as data:
        reader = csv.reader(data)
        next(reader)
        for line in list(reader):
            add_to_task_table({"library_name": line[0],
                               "paragraph": line[1],
                               "task": line[2],
                               "has_example": line[3],
                               "example_page": line[4],
                               "html_id": line[5]
                               })


def remove_old_tasks(library_name):
    mydb = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM overview_task WHERE library_name = '" + library_name + "'")
    cursor.close()
