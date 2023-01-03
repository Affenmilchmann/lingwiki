from threading import Thread, Event
from queue import Queue

from types import FunctionType
from typing import Iterator

from ._worker_threads import worker

class LingwikiThreadPool():
    def __init__(
        self,
        target_func: FunctionType,
        input_generator: Iterator,
        workers_amount: int,
        **target_func_args
    ):
        self.pool: list[Thread | None] = []
        self.target = target_func
        
        self.input_queue = Queue(maxsize=100)
        self.output_queue = Queue(maxsize=100)
        self.stop_flag = Event()
    
    def output_generator(self):
        yield None
        
    def __fill_pool(self, amount: int, **target_args):
        self.pool = [None] * amount
        for i in range(amount):
            self.pool[i] = Thread(
                worker,
                self.input_queue,
                self.output_queue,
                self.stop_flag,
                **target_args
            )
            
    def run_pool(self):
        for thr in self.pool:
            thr.run()
