from datetime import datetime
from airflow.decorators import dag, task


@dag(schedule_interval="@once", start_date=datetime(2022, 2, 1), catchup=False, tags=['training_dag'])
def training_dag():
    
    @task()
    def train_model():
        from core.models import Trainer

        trainer = Trainer(context={
            'buckets': {
            'train_bucket_name': 'sample-train-data',
            'val_bucket_name': 'sample-val-data'
            }
        })

        trainer.train()

        return True

    train_result = train_model()

_training_dag = training_dag()
