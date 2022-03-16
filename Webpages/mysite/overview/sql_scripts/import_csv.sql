LOAD DATA INFILE 'D:/PycharmProjects/TaskExtract/Webpages/mysite/overview/data/processed/orjson.csv' # CONCAT(...processed/', @library_name)
INTO TABLE overview_task
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;