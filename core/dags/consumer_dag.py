from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from core.operators import WorkerOperator


@dag(schedule_interval="@once", start_date=datetime(2022, 2, 1), catchup=False, tags=['consumer_dag'])
def consumer_dag():
    
    @task()
    def consume_images_to_minio():
        from core.kafka import Consumer
        from core.clients import MinioHandler

        worker = WorkerOperator(context={
            'tasks': Consumer(),
            'bucket_names': ['sample-train-data', 'sample-val-data'],
            'minio_client': MinioHandler()
        })

        context = get_current_context()
        worker.execute(context)

        return True

    consume_result = consume_images_to_minio()

_consumer_dag = consumer_dag()
