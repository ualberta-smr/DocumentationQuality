# Overview
This repository contains the source code and data to replicate the creation of a webtool prototype to measure software library documentation quality. The source code implementation of metrics is also provided. For this project we implement various metrics to evaluate documentation quality, and explore presenting the metrics in a summary that allows developers a quick understanding of the documentation quality for a library. The webtool allows users to submit a link to a library's online documentation and presents a summary with our calculated metrics. This will aid developers in deciding which library to integrate into their own project, based on the quality rating of the prospective library documentation without implemented metrics. 

This is the artifact for the anonymous MSR 2023 submission titled “Evaluating Software Documentation Quality”.

# What is in this repo:
This repository contains the source code for:

1. The Django webtool prototype that provides a summary and service that runs our implemented metrics on a given library documentation web link
2. The source code implementation for the different metrics
3. The data for the survey study we conducted using our webtool prototype
4. Scripts to analyze the responses of the built-in survey to the Django webtool
5. The ground truth datasets for both the task component (which includes the task extraction and task linking with code examples), and the documentation linking component, which compares the public source code methods/classes of a library with what is on its documentation, as well as whether the documentation contains a code example for that method/class.



## Data
- `Data` directory contains interview theming and coding
  - `Data/DocLinkingGT` contains CSVs with the extracted documentation code examples and source code references from different software libraries. Each of the CSVs contains information about what code/example was found, what documentation page it was found on, and what source code file it is referring to
  - `Data/Interview` contains coded responses from the interview study (not full transcripts) as well as a text document containing a summary of the free discussion section of the interview.
  - `Data/TaskComponent` contains CSVs with either manually extracted tasks from different library documentation pages, or the manually linked code examples with paragraphs from the library documentation.

- `Summary\survey\responses.csv` contains the raw survey data of all 173 unique session key accesses.

- `Summary\survey\responses_filtered.csv` contains filtered survey data of the 26 responses where at least 1 question was answered

## Important code files

- Original verb list for Task Extraction is found in this file:
`Summary/analyze/TaskExtractor/properties/config.properties`

- Updated verb lists for Task Extraction are found in this directory:
`Summary/analyze/TaskExtractor/properties`

- HCI Checklist Heuristics found in this file:
`Summary/analyze/HCI/checklist.py`

### Regex expressions
We use various regex expressions in our metric implementations. To match the different method calls for the different languages, the regex used can be found in the respective `<language>_matcher.py` file in the `Summary\analyze\MethodLinker` directory. For examples the regex used to match Python function calls can be found in `Summary\analyze\MethodLinker\python_matcher.py`.

# Installation Instructions
## Requirements
Python libraries are in the `requirements.txt` file. However, this project additionally needs:
1. MySQL Server 8.0 ([Installation guide](https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/), [Downloads](https://dev.mysql.com/downloads/mysql/))

## Installation

```
python -m nltk.downloader punkt
```

Before running the Django project, we need to create the database for the project to use. 
Django can automatically create SQLite databases, but not MySQL, so we need to do this ourselves.
First, run the MySQL service and access it through the command line
```
mysql -u root -p
```
Then create a database named "task_data"
```
create database task_data
```

To create a user in MySQL for this project to use, we can run the following commands in MySQL
```
CREATE USER 'djangouser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';

GRANT ALL ON task_data.* TO 'djangouser'@'localhost';

FLUSH PRIVILEGES;
```
**Note:** The MySQL configuration information used by the project is stored in `Summary/analyze/util.py` and `Summary/summary/my.cnf`.
The former is for use in the metric scripts, while the latter is for the Django project.

### Extra downloads
The program should automatically download any extra files needed to run the metric implementations, however, if unable to do so we make the `StringToTasks.jar` file, and `rsm.jar` available.

- [StringToTasks.jar](https://drive.google.com/file/d/19gV3aDLz5e6Gmb7nn29BlsfVX0AbHZ41/view?usp=sharing). Place the task extraction jar in `Summary/analyze/TaskExtractor`, (i.e., `Summary/analyze/TaskExtractor/StringToTasks.jar`).
- - [rsm.jar](https://drive.google.com/file/d/1S5tl8fFoZLbln8MsP-f6-F7K-F66HPZb/view?usp=share_link). Place the code readability jar to `Summary/analyze/Readability`, (i.e., `Summary/analyze/Readability/rsm.jar`).

## Running
Since this service is a Django project, the typical Django commands can be used to run this application.
```
Summary/manage.py makemigrations
Summary/manage.py migrate

# If running the server publicly
Summary/manage.py runserver
# If running the server through localhost
Summary/manage.py runserver --insecure
```
The project can now be accessed through a web browser
```
127.0.0.1:8000/docquality
```

### Locally
If you want to run the metric implementations locally you can run this Python file: `Summary/analyze.py` and include a call with your interested library documentation link. For example,
```python
# debug_metrics(language, library_name, doc_url, gh_url, domain)
debug_metrics("python", "orjson", "https://github.com/ijl/orjson", "https://github.com/ijl/orjson.git", "json")
```

Note that the MySQL database must still be setup (or you can modify method `debug_metrics` in `Summary/analyze/analyze.py` to print values instead). 

## Limitations
1. The service currently requires the library's GitHub repo to contain its source code in a `src` or `<library_name>` directory, otherwise the scripts are not able to find the source code. For example, NLTK stores its source code under the directory `nltk`, while CoreNLP stores its source code under a `src` directory.
