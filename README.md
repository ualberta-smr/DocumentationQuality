## Installation Instructions
### Requirements
Python libraries are in the `requirements.txt` file. However, this project additionally needs:
1. MySQL Server 8.0 ([Installation guide](https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/), [Downloads](https://dev.mysql.com/downloads/mysql/))

### Installation
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

Next we need to [download](https://drive.google.com/file/d/19gV3aDLz5e6Gmb7nn29BlsfVX0AbHZ41/view?usp=sharing) the task extraction jar to `Summary/analyze/TaskExtractor`, (i.e., `Summary/analyze/TaskExtractor/StringToTasks.jar`).

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
127.0.0.1:8000/overview
```

## Limitations
1. The service currently requires the library's GitHub repo to contain its source code in a `src` or `<library_name>` directory, otherwise the scripts are not able to find the source code. For example, NLTK stores its source code under the directory `nltk`, while CoreNLP stores its source code under a `src` directory.