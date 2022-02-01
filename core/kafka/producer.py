from aiokafka import AIOKafkaProducer
from core.config import KafkaProducerConfig
from airflow.models import Variable
import cv2
import asyncio
import threading
from core.interfaces import WorkerTask
import logging

class Producer(WorkerTask): 

    AIRFLOW_KEYS = ('topic', 'bootstrap_servers', 'value_serializer')

    def __init__(self):
        self.config = None
        self._done = threading.Event()
    
    def __repr__(self):
        return self.__class__.__name__

    async def _kafka_hook(self) -> AIOKafkaProducer:
        result = self._get_variables()
        if result:
            self.config = KafkaProducerConfig(**self.variables)
            consumer = AIOKafkaProducer(self.config.topic, self.config.asdict)
            return consumer
        self.config = KafkaProducerConfig()
        producer = AIOKafkaProducer(**self.config.asdict)
        return producer
    
    def _get_variables(self) -> bool:
        try:
            self.variables = {key: Variable.get(key) for key in self.AIRFLOW_KEYS}
            return True
        except KeyError as e:
            return False

    def is_task_active(self) -> bool:
        return True if self._done.is_set() else False

    def _set_task_status(self) -> None:
        self._done.set()
    
    async def start_task(self, *args, **kwargs):
        producer = await self._kafka_hook()
        await producer.start()
        is_queue = kwargs.get('queue', None)
        if is_queue is None:
            raise Exception("Could not obtain queue from context, aborting task")
        try:
            while not kwargs['queue'].empty():
                item = await asyncio.wait_for(kwargs['queue'].get(), 0.1)
                logging.info(f"Obtained frame from queue")
                if item is not None:
                    buf = cv2.imencode(".jpg", item)[1].tostring()
                await producer.send_and_wait(self.config.topic, buf)
                logging.info("Published message to topic")
        finally:
            await producer.stop()
            self._set_task_status()
            logging.info(f"Closing task {self.__class__.__name__}")
            kwargs['queue'].task_done()
