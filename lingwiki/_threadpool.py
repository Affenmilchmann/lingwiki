from types import FunctionType
from typing import Iterator

class ThreadPool():
    def __init__(self,
            thread_amount: int,
            target_func: FunctionType, passed_func: FunctionType,
            input_data: Iterator[str],
            **kwargs
        ) -> None:
        pass