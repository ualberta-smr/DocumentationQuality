
Command to export data from MySQL server. (Run in mysql-file-priv location)
```commandline
mysql -h localhost -u <user> -p -e 'select * from task_data.overview_response' | sed 's/\t/,/g' > responses.csv
```
