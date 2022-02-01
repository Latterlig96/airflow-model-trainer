from aiokafka import AIOKafkaConsumer
from core.config import KafkaConsumerConfig
import threading
import logging
from airflow.models import Variable
from core.interfaces import WorkerTask
import uuid
import numpy as np
import cv2

class Consumer(WorkerTask):

    AIRFLOW_KEYS = ('topic', 'bootstrap_servers',
                    'enable_auto_commit', 'value_deserializer')

    def __init__(self):
        self.config = None
        self._done = threading.Event()

    def __repr__(self):
        return self.__class__.__name__

    async def _kafka_hook(self) -> AIOKafkaConsumer:
        result = self._get_variables()
        if result:
            self.config = KafkaConsumerConfig(**self.variables)
            consumer = AIOKafkaConsumer(self.config.topic, self.config.asdict)
            return consumer
        self.config = KafkaConsumerConfig()
        consumer = AIOKafkaConsumer(self.config.topic, **self.config.asdict)
        return consumer
    
    def _get_variables(self) -> bool:
        try:
            self.variables = {key: Variable.get(key) for key in self.AIRFLOW_KEYS}
            return True
        except KeyError as e:
            return False    

    def is_task_active(self) -> bool:
        return True if self._done.is_set() else False
    
    def set_task_status(self) -> None:
        self._done.set()

    async def start_task(self, *args, **kwargs) -> None:
        consumer = await self._kafka_hook()
        await consumer.start()
        minio_client = kwargs.get('minio_client', False)
        if not minio_client:
            raise ValueError("Could not obtain minio client, task exiting")
        bucket_name = kwargs.get('bucket_name', None)
        bucket_names = kwargs.get('bucket_names', None)
        if bucket_name is not None:
            minio_client.create_bucket(kwargs['bucket_name'])
        if bucket_names is not None:
            for _bucket_name in kwargs['bucket_names']:
                minio_client.create_bucket(_bucket_name)
        try:
            async for msg in consumer:
                _id = uuid.uuid4()
                buf = np.frombuffer(msg.value, np.uint8)
                img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
                _bn = bucket_name if bucket_name is not None else np.random.choice(bucket_names)
                object_name = ".".join([_id.hex + '_' + str(np.random.choice([0, 1])), 'jpg'])
                minio_client.put_object_to_bucket(bucket_name=_bn,
                                                object_data=img,
                                                object_name=object_name)
        finally:
            await consumer.stop()
            logging.info(f"Closing task {self.__class__.__name__}")
            self.set_task_status()
