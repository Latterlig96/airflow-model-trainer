#!/bin/bash

psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE DATABASE mlflow;
    GRANT ALL PRIVILEGES ON DATABASE mlflow TO postgres;
EOSQL

echo "Created database mlflow for user postgres";
