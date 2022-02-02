from airflow.models.baseoperator import BaseOperator
from typing import Dict, Any
from core.interfaces.interface import WorkerTask
from core.workers.worker import WorkerManager
import logging
from typing import TypeVar, List
import asyncio

AirflowContext = TypeVar('AirflowContext')

class WorkerOperator(BaseOperator):

    def __init__(self,
                 context: Dict[Any, Any]):
        self._manager: WorkerManager = WorkerManager()
        created = self._set_tasks(context['tasks'])
        if not created:
            logging.error("Something went wrong while registering tasks, please check your configuration")
        self._set_context(context)
    
    async def _execute_async(self) -> bool:
        result = await self._manager.start()
        return result
    
    def _set_context(self, context: Dict[Any, Any]) -> None:
        self._manager.init_context(context)
    
    def _set_tasks(self, tasks: List[WorkerTask]) -> bool:
        created = self._manager.register_tasks(tasks)
        return created 

    def execute(self, context: AirflowContext) -> None:
        asyncio.run(self._execute_async())
