import os
import re
from shutil import rmtree

from git import Repo

EXTENSION = re.compile(r"\.py$|\.pyi$")


def clone_repo(repo_url, clone):
    repo_regex = re.compile(r"(?<=/)[a-zA-Z.-]+(?!/)$")
    try:
        repo_name = re.search(repo_regex, repo_url)[0]
        if repo_name[-4:] == ".git":
            repo_name = repo_name[:-4]
        else:
            repo_url = repo_url + ".git"
        repo_path = os.path.abspath("../analyze_library/cloned_repos/" + repo_name)
        if clone:
            if not os.path.exists(repo_path):
                # rmtree(repo_path, onerror=rmtree_access_error_handler)
                Repo.clone_from(repo_url, repo_path)
    except Exception as e:
        repo_path = None
    return repo_path


def rmtree_access_error_handler(func, path, exc_info):
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def get_source_files(repo_name, repo_path):
    source_files = []
    src_dir = None
    # Only look at the top level directory in this loop
    for root, dirs, files in os.walk(repo_path):
        for dir_name in dirs:
            if dir_name.lower() == "src" or dir_name.lower() == repo_name.lower():
                src_dir = os.path.normpath(root + "/" + dir_name)
                break
        for file in files:
            if re.search(EXTENSION, file) and "test" not in file.lower():
                source_files.append(os.path.normpath(root + "/" + file))
        break
    # If we found a src directory, loop through all the files (subdirectory too)
    if src_dir:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if root == "test":
                    break
                if re.search(EXTENSION, file) and "test" not in file.lower():
                    source_files.append(os.path.normpath(root + "/" + file))
    return source_files
