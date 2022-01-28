import asyncio
import logging
from core.interfaces import WorkerTask
from typing import List, Union

class WorkerManager:

    def __init__(self):
        self._tasks: WorkerTask = []
        self._context = None

    def register_tasks(self, tasks: Union[List[WorkerTask], WorkerTask]) -> Union[bool, Exception]:
        if isinstance(tasks, list):
            if all(isinstance(x, WorkerTask) for x in tasks):
                for task in tasks:
                    self._tasks.append(task)
                logging.info("Tasks has been registered")
                return True
            raise ValueError("""Some of the provided instances are not WorkerTask instances, 
                              could not proceed further""")
        elif not isinstance(tasks, WorkerTask):
            raise ValueError("""Some of the provided instances are not WorkerTask instances, 
                              could not proceed further""")
        logging.info("Tasks has been registered")
        self._tasks.append(tasks)
        return True

    def init_context(self, context):
        logging.info(f"Initializing context for tasks {self._tasks}")
        self._context = context

    async def start(self):
        results = await asyncio.gather(*[task.start_task(**self._context) for task in self._tasks],
                                        return_exceptions=True)
        logging.info(results)
        logging.info("Tasks completed successfully")
        return True
