import lingwiki
from requests.exceptions import RequestException
from time import sleep
from threading import Thread
from time import sleep, time
from logging import log, INFO
from typing import Generator

from ipywidgets import Output, HBox, VBox, IntProgress

__progress_widget: HBox = None
__out_txt: Output = None
__out_mem: Output = None
__out_page_speed: Output = None
__out_bar: IntProgress = None
__out_bar_txt: Output = None

#
#   VISUALS
#
lingwiki.set_language('ru')

def get_widget() -> HBox:
    """
    # Returns ipywidgets.HBox. 
    its progress bar can be modified with following methods:
     - update_bar_val()
     - update_bar_max()
     - update_bar_desc()
     - update_bar_done()
     - update_bar_notdone()

    also upper text from the left widget box is editable with
     - update_text_status()

    additionaly you may add set text between upper and lower texts in left box
     - update_text_info()

    These methods will do nothing if called before get_widget()

    """
    global __out_txt, __out_mem, __out_page_speed, __out_bar, __out_bar_txt, __progress_widget

    __out_txt = Output(layout={'width': '92%', 'margin': 'auto'})
    __out_mem = Output(layout={'width': '92%', 'margin': 'auto'})
    __out_page_speed = Output(layout={'width': '92%', 'margin': 'auto'})
    __out_bar = IntProgress(
        layout={'width': '80%', 'margin': 'auto'}, 
        description="?/?", 
        style={'description_width': 'initial'}
    )
    __out_bar_txt = Output(layout={'margin': 'auto'})
    txt_box = VBox([__out_txt, __out_mem, __out_page_speed], layout={'border': '1px solid black', 'width': '50%'})
    bar_box = VBox([__out_bar_txt, __out_bar], layout={'width': '50%'})

    __progress_widget = HBox([txt_box, bar_box])
    return __progress_widget

def __update_txt(text, out):
    if out == None:
        return
    out.clear_output(wait=True)
    with out:
        print(text)

def update_text_status(val):
    global __out_txt
    __update_txt(val, __out_txt)

def update_text_info(val):
    global __out_mem
    __update_txt(val, __out_mem)

def update_bar_val(val: int):
    """set a bar int value"""
    global __out_bar
    if __out_bar == None: return
    __out_bar.value = val
    __out_bar.description = f"{__out_bar.value}/{__out_bar.max}"

def update_bar_max(val: int):
    """set a bar maximum int value"""
    global __out_bar
    if __out_bar == None: return
    __out_bar.max = val

def update_bar_desc(val: str):
    """set bar description"""
    global __out_bar
    if __out_bar == None: return
    __out_bar.description = val

def update_bar_done():
    """set bar as finished"""
    global __out_bar
    if __out_bar == None: return
    __out_bar.bar_style = 'success'
    __out_bar.value = __out_bar.max
    __out_bar.description = f"{__out_bar.value}/{__out_bar.max}"

def update_bar_notdone():
    """reset bar to normal state"""
    global __out_bar
    if __out_bar == None: return
    __out_bar.value = 0
    __out_bar.bar_style = ''

#
#   WIKI MODULE
#

def get_random_page(page_buffer, page_index):
    try:
        page_buffer[page_index] = ''.join(p for p in lingwiki.article(return_paragraphs=True, attempts_limit=0)['paragraphs'])
    except RequestException as e:
        page_buffer[page_index] = None
        print(f"[RequestException] pausing for 10sec...")
        sleep(10)

#
#   THREADING
#

def __copy_buffer(buffer_to_copy: list[str], buffer: list[str]):
    buffer.clear()
    for item in buffer_to_copy:
        if type(item) is str:
            buffer.append(item)
    
def __join_pages(buffer: list[str]) -> str:
    return ''.join([f"{page}\n" for page in buffer if type(page) is str])

def __start_threads(buffer, amount=50) -> list[Thread]:
    threads = []
    buffer.clear()
    for i in range(amount):
        buffer.append(False)
        t = Thread(target=get_random_page, args=(buffer, i))
        threads.append(t)
        threads[i].start()
    return threads

def __wait_threads(threads):
    for t in threads:
        t.join()

#
#   WIKI PAGES GENERATOR
#

def pages(page_amount, buffer_size=1, retry_failed_pages=False) -> Generator[str, None, None]:
    """
    Generator that downloads and yields string with 'buffer_size' random pages joined in one string.
    It loads pages in amount of 'buffer_size' in separate threads and joins them in a string.
    So you dont have to wait for 2 seconds for every page to load like if you were using a single thread.
    It also loads them while your code is running. So if its relatively slow, the next yield will
    probably be ready when you ask for next output

    Note: if 'page_amount' < 'buffer_size' then 'buffer_size' will be set to max(page_amount//100, 1)

     - 'page_amount': amount of random wikipedia pages you want to get. It is guaranteed to
     give you at least asked amount. It probably will give you more
     - 'buffer_size': amount of pages that will be loaded simultaneously and yielded to you joined 
     in a single string. 
    """
    global __out_txt, __out_page_speed, __out_bar_txt

    if page_amount < buffer_size:
        buffer_size = max(page_amount//100, 1)

    wait_time = 5
    processed_pages = []
    thr_page_buffer = []
    page_buffer = []
    thread_list = []
    i = 0
    
    thread_list = __start_threads(thr_page_buffer, buffer_size)
    
    begin_time = time()
    while i < page_amount:
        current_buffer_size = min(buffer_size, page_amount-i)
        log(INFO, "Downloading {current_buffer_size} pages...")
        # visuals
        __update_txt(f"{round(buffer_size/(max(time() - begin_time, 1)), 2)} page/s", __out_page_speed)
        __update_txt(
            "Waiting for {}/{} pages to finish downloading...".format(
                sum([1 for page in thr_page_buffer if page == False]),
                current_buffer_size,
            ), 
            __out_txt
        )
            
        # threading
        __wait_threads(thread_list)
        __copy_buffer(thr_page_buffer, page_buffer)
        
        if len(thr_page_buffer) == 0:
            __update_txt(f"All pages failed to load. Waiting for {wait_time}min...", __out_txt)
            sleep(wait_time * 60)
        thread_list = __start_threads(thr_page_buffer, current_buffer_size)
        # preparing for yielding
        begin_time = time()
        # visuals
        __update_txt(
            "Done {}/{}.\nLoaded {} failed to load".format(
                i, page_amount,
                max(0, len(thr_page_buffer) - len(page_buffer)),
            ), 
            __out_bar_txt
        ) 
        # yielding
        i += 1

        # visuals 
        if i >= page_amount:
            __update_txt(
                "Done {}/{}.\n{} failed to load".format(
                    i, page_amount,
                    max(0, len(thr_page_buffer) - len(page_buffer)),
                ), 
                __out_bar_txt
            ) 

        yield __join_pages(page_buffer)


for page_text in pages(3):
    words = page_text.split(" ")
    print(f"{len(words)} words\t{''.join(w+' ' for w in words[:7])}...")