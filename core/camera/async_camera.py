import asyncio
import typing
from core.interfaces import WorkerTask
import cv2
import threading
import logging

AsyncQueue = typing.TypeVar('AsyncQueue')

class AsyncCamera(WorkerTask):

    def __init__(self):
        self._done = threading.Event()
    
    def __repr__(self):
        return self.__class__.__name__
    
    def _set_camera(self, source: str) -> typing.TypeVar('OpencvCamera'):
        try:
            camera = cv2.VideoCapture(source)
            return camera
        except Exception as e:
            logging.exception(e)
        
    def set_task_status(self) -> None:
        self._done.set()
    
    def is_task_active(self) -> bool:
        return self._done.is_set()
    
    async def start_task(self, *args, **kwargs) -> None:
        camera = self._set_camera(kwargs['stream'])
        try:
            while not self._done.is_set() and camera.isOpened():
                ret, frame = camera.read()
                if not ret:
                    self.set_task_status()
                await kwargs['queue'].put(frame)
                await asyncio.sleep(0.1)
        finally:
            self.set_task_status()
            is_queue = kwargs.get('queue', False)
            if not is_queue:
                kwargs['queue'].task_done()
