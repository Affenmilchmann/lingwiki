from time import time
from requests import get
from bs4 import BeautifulSoup

from .wiki_threads import ThreadPool
from .wiki_threadfuncs import get_article_target

__category_blacklist = list()

class DiffBuffer():
    def __init__(self, size=10, last_val=0) -> None:
        self.__list = [0]*size
        self.__list_sum = 0
        self.__size = size
        self.__i = 0
        self.__last_val = last_val
    def update(self, next_val) -> float:
        self.__list_sum -= self.__list[self.__i]
        self.__list[self.__i] = next_val - self.__last_val
        self.__list_sum += self.__list[self.__i]
        self.__last_val = next_val
        self.__i %= self.__size
        return self.__list_sum / self.__size

item_progress_buffer = DiffBuffer()
time_progress_buffer = DiffBuffer(last_val=time())

def __print_progress(done_count, target_count, bar_lenght=20, done_ch="#", pending_ch="_"):
    avrg_items_per_iter = item_progress_buffer.update(done_count)
    avrg_iter_time = time_progress_buffer.update(time())
    avrg_item_per_sec = avrg_items_per_iter / avrg_iter_time
    sec_left = (target_count - done_count) / avrg_item_per_sec
    pass

def get_category_blacklist() -> list[str]:
    """returns current list of words that will be ignored if found in categories names"""
    returned_list = list()
    for category in __category_blacklist:
        returned_list.append(category)
    return returned_list

def add_category_blacklist(category: str) -> bool:
    """
    Adds 'category' to the blacklist word list. Page will be ignored if any word is found in category name.
    returns True if category added. False if the input word is already listed
    """
    if category in __category_blacklist:
        return False
    __category_blacklist.append(category)

def set_category_blacklist(ctgr_list: list[str]) -> None:
    """Set a list of blacklist words. Page will be ignored if any word is found in category name."""
    __category_blacklist.clear()
    for category in ctgr_list:
        __category_blacklist.append(category)

def __get_html_file(timeout=10, url=None, lang='en'):
    headers = {'Accept-Encoding': 'identity'}
    url = url if url else f"https://{lang}.wikipedia.org/wiki/special:random"
    r = get(url, headers=headers, timeout=timeout)
    return r.text

def __is_blacklisted(article_categories, blacklisted_categories) -> bool:
    return bool(set(article_categories).intersection(blacklisted_categories))

def get_article(url=None, lang='en', attempts_limit=0, timeout=10, **kwargs) -> dict[str, str|dict|None]:
    """
    Returns a dict with article content.
    If you need multiple articles use `articles_flow()`,
    it will save you a lot of time

    Params
    -------
    - `url`: str - url to wikipedia page. If None, returns random article.
    `lang` and blacklisted categories [TODO link to docs] are ignored if url is present.
    - `attempts_limit`: int - amount of retries if request failed or returned page had blacklisted category
    (for random pages only)
    - `timeout`: int - request timeout in seconds
    - `lang`: str - articles language (for random pages only)
    
    kwargs
    -------
    Boolean arguments that indicate which content will be included in a returned dict.
    Arg names match dict keys.

    [ ! Important ! ] Type after arrow shows what type the returned content will have
    - `title` -> str
    - `paragraphs` -> list[str]
    - `categories` -> list[str]
    - `image_links` -> list[str]
    - `article_links` -> list[str] - links that article page has in it. NOT the links to articles.
    Use `articles_flow()` if you want to get multiple articles with links
    
    Failed returns
    --------------

    Will try to get another page till it finds fitting page or reaches `attempts_limit`.

    - Returns None after reaching `attempts_limit`
    - Raises RequestError if request failed
    """
    if attempts_limit < 0: return None

    soup = BeautifulSoup(
                __get_html_file(timeout=timeout, url=url, lang=lang),
                'html.parser'
        )
    raw_categories = soup.find(id = 'mw-normal-catlinks').find_all('li')
    if not url and __is_blacklisted(raw_categories): 
        return get_article(
                url, lang,
                attempts_limit=attempts_limit-1,
                timeout=timeout,
                **kwargs
            )

    article_content = {
        'url': None,
        'title': True,
        'paragraphs': False,
        'categories': False,
        'images': False,
        'links': False
    }
    article_content.update(kwargs)

    return_dict = {}

    if article_content['title']: return_dict['title'] = soup.find(id="firstHeading").get_text()
    if article_content['paragraphs']: return_dict['paragraphs'] = [p.get_text() for p in soup.find_all('p')]
    if article_content['categorits']: return_dict['categorits'] = [p.get_text() for p in raw_categories]
    if article_content['images']: return_dict['images'] = [raw_img['src'] for raw_img in soup.find_all('img')]
    # TODO if article_content['title']: 

    return return_dict

def articles_flow(
        amount: int, threads_amount: int = 10,
        buffer_size: int = 30, batch_size: int = 1,
        req_limit=0, url=None, timeout=10,
        lang='en',
        
    ):
    # # # # # # # # # # # # # # # 
    #         THREADING         #
    thread_pool = ThreadPool(
            buffer_size=buffer_size,
            threads_amount=threads_amount, 
            batch_size=batch_size, 
            target_func=get_article_target,
            threaded_func=get_article,
            **article_settings,
        )
    # # # # # # # # # # # # # # # 
    #         MAIN LOOP         #
    articles_returned = 0
    while articles_returned < amount:
        limited_batch_size = None if amount - articles_returned > batch_size else amount - articles_returned
        batch = thread_pool.get_articles_from_queue(limited_batch_size)
        articles_returned += len(batch)
        yield batch
    del thread_pool

if __name__ == "__main__":
    print(get_article(get_paragraphs=True))
    """c = 0
    for batch in articles_flow(1000, threads_amount=20, batch_size=15):
        c += 1
        print(len(batch), c)"""
