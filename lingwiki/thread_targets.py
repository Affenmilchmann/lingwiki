from threading import Event
from queue import Queue
from types import FunctionType

def get_article_target(
        threaded_func: FunctionType,
        article_queue: Queue,
        keep_alive: Event,
        **article_settings):

    while keep_alive.is_set():
        article = threaded_func(**article_settings)
        article_queue.put(article)