from queue import Queue
from types import FunctionType
from threading import Event

def worker(
        target_func: FunctionType,
        url_in_queue: Queue,
        article_out_queue: Queue,
        stop_flag: Event, 
        **kwargs):
    """Process URL tasks in a worker thread.
    
    Parameters:
    target_func [FunctionType]: The function to use to process the URL.
    url_in_queue [queue.Queue]: The input queue containing the URL tasks.
    article_out_queue [queue.Queue]: The output queue to store the results.
    stop_flag [threading.Event]: The event flag to signal the worker to stop.
    **kwargs: Additional keyword arguments to pass to `target_func`.
    """
    
    
    while not stop_flag.is_set():
        url = url_in_queue.get()
        if url is None: break
        
        result = target_func(url, **kwargs)
        article_out_queue.put(result)
        url_in_queue.task_done()
