import traceback
from datetime import datetime

import mysql.connector

from analyze_library.models.lib_overview import LibraryOverview

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "user": "lib-analysis-user",
    "password": "password",
    "database": "lib_analysis"
}


def save_lib_overview_to_db(library_overview: LibraryOverview):
    item_dict = dict(library_overview)
    item_dict["last_updated"] = datetime.utcnow()
    website_db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = website_db.cursor()
    column_names = []
    values = []
    for key, value in item_dict.items():
        column_names.append(key)
        values.append(value)
    query = "SELECT * FROM doc_quality_analysis_app_library WHERE library_name = '" + str(item_dict["library_name"]) + "';"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        query = "UPDATE doc_quality_analysis_app_library SET "
        for i in range(len(column_names)):
            query += column_names[i] + " = %s, "
        query = query[:-2] + " WHERE library_name = '" + item_dict["library_name"] + "'"
    else:
        query = "INSERT INTO doc_quality_analysis_app_library ("
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
    except Exception as e:
        print("FAILED TO SAVE TO DB")
        print(traceback.format_exc())
        print(query)
