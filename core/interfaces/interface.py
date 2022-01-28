import abc

class WorkerTask(abc.ABC):

    async def start_task(self, *args, **kwargs):
        raise NotImplementedError

    def is_task_active(self):
        raise NotImplementedError

    def set_task_status(self):
        raise NotImplementedError
