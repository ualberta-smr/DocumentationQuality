#!/bin/bash

## script name; import_Script.sh

ARGS=2

if [ $# -ne "$ARGS" ]
then

 echo "you passed $# parameters"
 echo "Usage: `basename $0` import_csv.sql library_name"

exit
fi
sql_script=$1
library_name=$2

#run mysql query with paramenters

/usr/bin/mysql –uuser_id -ppassword –h mysql-host -A -e "set @library_name=${library_name}; source ${sql_script};";

exit

# end of script.

# Example:
# Usage: import_script.sh import_csv.sql <library_name>
# import_script.sh import_csv.sql orjson