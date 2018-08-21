#!/bin/bash

DB_NAME='news'
DB_SOURCE='https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip'

if ! command -v psql > /dev/null; then
    >&2 echo "This script requires psql, but it is not installed.  Aborting."
    exit 1
fi

# Thanks to: https://stackoverflow.com/a/32084118
if psql --quiet --list --tuples-only --no-align | grep -q "^$DB_NAME|"; then
    echo "A '$DB_NAME' database already exists!  Exiting."
    exit 0
fi


echo "Creating '$DB_NAME' database."
# Assume createdb exists, since it comes with psql
createdb "$DB_NAME"


echo "Importing data into '$DB_NAME' database.  This may take a while."
# Assume curl and funzip are installed
curl -sL "$DB_SOURCE" | funzip | psql --dbname "$DB_NAME" --file -


echo "The '$DB_NAME' database is all set up!"
