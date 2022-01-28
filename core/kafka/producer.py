from aiokafka import AIOKafkaProducer
from core.config import KafkaProducerConfig
from airflow.models import Variable
import cv2
import asyncio
import threading
from core.interfaces import WorkerTask

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
        try:
            while not kwargs['queue'].empty():
                await asyncio.sleep(0.1)
                item = await kwargs['queue'].get()
                if item is not None:
                    buf = cv2.imencode(".jpg", item)[1].tostring()
                await producer.send_and_wait(self.config.topic, buf)
                await asyncio.sleep(0.1)
        finally:
            await producer.stop()
            self._set_task_status()
            is_queue = kwargs.get('queue', False)
            if not is_queue:
                kwargs['queue'].task_done()
