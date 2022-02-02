from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from core.operators import WorkerOperator


@dag(schedule_interval="@once", start_date=datetime(2022, 2, 1), catchup=False, tags=['producer_dag'])
def producer_dag():
    
    @task()
    def publish_images_to_topic():
        import asyncio
        from core.camera import AsyncCamera
        from core.kafka import Producer

        worker = WorkerOperator(context={
            'queue': asyncio.Queue(maxsize=200),
            'stream': './videos/example.mp4',
            'tasks': [AsyncCamera(), Producer()]
        })

        context = get_current_context()
        worker.execute(context)

        return True

    produce_result = publish_images_to_topic()
    
_producer_dag = producer_dag()
