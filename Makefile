.EXPORT_ALL_VARIABLES:

AIRFLOW_HOME=$(shell pwd)/airflow
PYTHONPATH=$(shell pwd)
AIRFLOW__CORE__DAGS_FOLDER=$(shell pwd)/core/dags/

build:
	sudo docker-compose up --build -d

requirements:
	pip install -r requirements.txt

db:
	bash -c "airflow db upgrade"
	bash -c "airflow users create -e admin@admin.org -f admin -l admin -r Admin -u admin -p admin"

scheduler:
	bash -c "airflow scheduler"

webserver:
	bash -c "airflow webserver"
