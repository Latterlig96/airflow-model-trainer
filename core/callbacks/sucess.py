from typing import TypeVar

_AirflowContext = TypeVar('_AirflowContext')

def on_success_callback(context: _AirflowContext):
    raise NotImplementedError
