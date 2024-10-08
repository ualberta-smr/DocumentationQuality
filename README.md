# Overview
To access the artifact for the MSR 2023 paper titled "Evaluating Software Documentation Quality" by Henry Tang and Sarah Nadi use [v1.0](https://github.com/ualberta-smr/DocumentationQuality/tree/v1.0).
We implement various metrics to evaluate documentation quality, and explore presenting the metrics in a summary (webtool) that allows developers a quick understanding of the documentation quality for a library. The webtool allows users to submit a link to a library's online documentation and presents a summary with our calculated metrics. This will aid developers in deciding which library to integrate into their own project, based on the quality rating of the prospective library documentation without implemented metrics. 

# What is in this repo:
This repository contains:

1. The source code for the Django webtool prototype that provides a summary and service that runs our implemented metrics on a given library documentation web link
2. The source code implementation for the different metrics
3. The data for the survey study we conducted using our webtool prototype
4. Script to analyze the responses of the built-in survey to the Django webtool
5. The ground truth datasets for both the task-related component (which includes the task extraction and task linking with code examples), and the documentation linking component, which compares the public source code methods/classes of a library with what is in its documentation, as well as whether the documentation contains a code example for that method/class.
6. Data of our interview coding 
7. Data of our intermediate steps from analyzing existing literature to defining documentation aspects and selecting documentation aspects
8. A MySQL database dump of evaluated library documentation



## Data Structure
- The `Data` directory contains interview theming and coding
  - `Data/DocLinkingGT` contains CSVs with the extracted documentation code examples and source code references from different software libraries. Each of the CSVs contains information about what code/example was found, what documentation page it was found on, and what source code file it is referring to.
  - `Data/Interview` contains coded responses from the interview study (not full transcripts) as well as a text document containing a summary of the free discussion section of the interview.
  - `Data/TaskComponent` contains CSVs with either manually extracted tasks from different library documentation pages, or the manually linked code examples with paragraphs from the library documentation.
  - `Data/DocumentationAspects` contains CSVs which show out intermediate steps in aggregating the existing literature and extracting and defining documentation aspects that we later filter and decide which to create/find metrics for
  - `Data/task_data.sql` contains a MySQL dump of the database used to store the evaluation of our metrics on various software libraries during the course of the survey study. It also contains the raw survey responses.

- `Summary/survey/responses.csv` contains the raw survey data of all 173 unique session key accesses.

- `Summary/survey/responses_filtered.csv` contains filtered survey data of the 26 responses where at least 1 question was answered

## Important code files

- Original verb list for Task Extraction is found in this file:
`Summary/analyze/TaskExtractor/properties/config.properties`

- Updated verb lists for Task Extraction are found in this directory:
`Summary/analyze/TaskExtractor/properties/`

- HCI Checklist Heuristics found in this file:
`Summary/analyze/HCI/checklist.py`

### Regex expressions
We use various regex expressions in our metric implementations. To match the different method calls for the different languages, the regex used can be found in the respective `<language>_matcher.py` file in the `Summary/analyze/MethodLinker/` directory. For example, the regex used to match Python function calls can be found in `Summary/analyze/MethodLinker/python_matcher.py`.

# Installing and Running the Web tool (locally)

## Requirements
Python dependencies are in the `requirements.txt` file. Please run `python install -r requirements.txt`. This project additionally needs:
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
The program should automatically download any extra files needed to run the metric implementations, however, if unable to do so we make the `StringToTasks.jar` file, and `rsm.jar` available [here](https://zenodo.org/records/10951436).

- StringToTasks.jar. Place the task extraction jar in `Summary/analyze/TaskExtractor`, (i.e., `Summary/analyze/TaskExtractor/StringToTasks.jar`).
- rsm.jar. Place the code readability jar to `Summary/analyze/Readability`, (i.e., `Summary/analyze/Readability/rsm.jar`).

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

### Loading the database
To load the database with our provided existing data, you can run:

`mysql -u [user] -p task_data < Data/task_data.sql`

### Separately triggering metrics scripts
If you want to run the metric implementations separately from running the webpage you can run this Python file: `Summary/analyze.py` and include a call with your interested library documentation link. For example,
```python
# debug_metrics(language, library_name, doc_url, gh_url, domain)
debug_metrics("python", "orjson", "https://github.com/ijl/orjson", "https://github.com/ijl/orjson.git", "json")
```

Note that the MySQL database must still be setup (or you can modify method `debug_metrics` in `Summary/analyze/analyze.py` to print values instead). 

The debug_metrics method can also be modified to include or exclude which metrics you want to run by commenting out the call to that metric. By default, all metrics are run and database updates are made.

# Analyzing the survey data
The survey script to analyze survey responses can be found in this directory:
`Summary/survey/main.py`.

You can simply run `./main.py` in this directory to run the script with the `responses.csv` and `responses_filtered.csv` found in the same directory. This will create (or update) the plots found in the `Summary/survey/plots/` directory.


## Limitations
1. The service currently requires the library's GitHub repo to contain its source code in a `src` or `<library_name>` directory, otherwise the scripts are not able to find the source code. For example, NLTK stores its source code under the directory `nltk`, while CoreNLP stores its source code under a `src` directory.

# Contact
If you have any questions or concerns, you can open an Issue using Github's issue tracker, or email:

- Henry Tang <hktang@ualberta.ca>, or 
- Sarah Nadi <nadi@ualberta.ca>
