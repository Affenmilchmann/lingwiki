from threading import Thread, Event
from queue import Queue
from time import sleep, time
from types import FunctionType

class ThreadPool():
    def __init__(self, 
            threads_amount: int,
            buffer_size: int, batch_size: int,
            target_func: FunctionType, threaded_func: FunctionType,
            **article_settings
        ) -> None:
        if threads_amount > 100: pass # LOGGER warning
        self.__target_func = target_func
        self.__threaded_func = threaded_func
        self.__keep_alive = Event(); self.__keep_alive.set()
        self.__queue = Queue(buffer_size)
        self.__threads: list[Thread] = []

        if batch_size == None:
            self.__batch_size = 1
        else:
            self.__batch_size = batch_size
            if self.__batch_size <= 0: raise AttributeError("Min batch size must be > 0")

        for i in range(threads_amount):
            t = Thread(
                target=self.__target_func,
                args=(
                    self.__threaded_func,
                    self.__queue,
                    self.__keep_alive
                ),
                kwargs=article_settings,
            )
            self.__threads.append(t)
            self.__threads[i].start()

    def get_articles_from_queue(self, change_size = None) -> str | list[str]:
        try:
            if self.__batch_size == 1:
                return self.__queue.get()
            else:
                return [self.__queue.get() for _ in range(change_size if change_size else self.__batch_size)]
        except Exception as e:
            print(e.with_traceback())
            self.__del__()

    def get_queue_filled_size(self) -> int:
        return self.__queue.qsize()

    def __del__(self, timeout: int=20, check_every: float=1) -> None:
        self.__keep_alive.clear()
        b_time = time()
        alive_count = len(self.__threads)
        # LOGGER terminating threads
        for t in self.__threads: t.join()
        while time() - b_time < timeout and alive_count > 0:
            alive_count = 0
            for t in self.__threads:
                alive_count += int(t.is_alive())
            # LOGGER alive count
            sleep(check_every)
        # LOGGER failed to terminate threads
