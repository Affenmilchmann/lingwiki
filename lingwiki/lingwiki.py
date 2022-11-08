from time import time
from requests import get
from bs4 import BeautifulSoup

from wiki_threads import ThreadPool
from wiki_threadfuncs import get_article_target

category_blacklist = list()

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
    for category in category_blacklist:
        returned_list.append(category)
    return returned_list

def add_category_blacklist(category: str) -> bool:
    """
    Adds 'category' to the blacklist word list. Page will be ignored if any word is found in category name.
    returns True if category added. False if the input word is already listed
    """
    if category in category_blacklist:
        return False
    category_blacklist.append(category)

def set_category_blacklist(ctgr_list: list[str]) -> None:
    """Set a list of blacklist words. Page will be ignored if any word is found in category name."""
    category_blacklist.clear()
    for category in ctgr_list:
        category_blacklist.append(category)

def __get_html_file(timeout=10, url=None, lang='en'):
    headers = {'Accept-Encoding': 'identity'}
    url = url if url else f"https://{lang}.wikipedia.org/wiki/special:random"
    r = get(url, headers=headers, timeout=timeout)
    return r.text

def __parse_html(**article_settings) -> dict[str, str|dict|None]:
    settings = {
        'rec_limit': 0, 'timeout': 10,
        'url': None, 'lang': 'en',
        'get_title': True, 'get_paragraphs': False,
        'get_categories': False, 'get_images': False,
        'get_infobox': False,
    }
    settings.update(article_settings)
    if settings['rec_limit'] < 0:
        return None

    soup = BeautifulSoup(
        __get_html_file(
                timeout=settings['timeout'], 
                url=settings['url'],
                lang=settings['lang'],
            ),
            'html.parser'
        )
    raw_categories = soup.find(id = 'mw-normal-catlinks').find_all('li')
    category_list = [cat.get_text() for cat in raw_categories]
    for blacklisted_category in category_blacklist:
        for category in category_list:
            if blacklisted_category in category:
                return None

    return_dict = {}

    if settings['get_title']:
        title = soup.find(id="firstHeading").get_text()
        return_dict['title'] = title
    if settings['get_paragraphs']:
        raw_paragraphs = soup.find_all('p')
        return_dict['paragraphs'] = [p.get_text() for p in raw_paragraphs]
    if settings['get_categories']: 
        raw_categories = soup.find(id = 'mw-normal-catlinks').find_all('li')
        return_dict['categorits'] = [p.get_text() for p in raw_categories]
    if settings['get_infobox']:
        # may be implemented
        pass
    if settings['get_images']: 
        soup.find_all('img')
        return_dict['images'] = [raw_img['src'] for raw_img in soup.find_all('img')]

    return return_dict

def get_article(**article_settings) -> dict[str, str|dict|None] | None:
    """
    Summary
    ----------
    Returns a dict of wikipedia's article content.

    If `url` is set, will try to parse article by this url !!! ignoring blacklisted categories too !!! 

    Otherwise will parse random article skipping articles with blacklisted categories.
    (see `get_category_blacklist()`, `set_category_blacklist()`, `add_category_blacklist()`)

    You can set articles language with `set_language()`

    Params
    ----------
    - `attempts_limit` - amount of retries if request failed or returned page had blacklisted category
    - `timeout` - request timeout
    - `get_<name>` - select what article content you want to be included in returned dict

    Return
    ----------
    - Returns a dict

    {
        'title': str | None, - article title
        'paragraphs': {
            'title': str | None,- title of the paragraph
            'text_content': str | None,     - text of the paragraph
        },
        'categories' : list[str] | None,     - list of article's categories
        'infobox': {
            'title': str | None,
            'content': str | None, - unparsed html text. There are too many variations of contents
        }
        'images': list[str], - list of article's image links. 
    }
    
    Failed returns
    --------------

    Will try to get another page till it finds fitting page or reaches `attempts_limit`.

    - Returns None after reaching `attempts_limit`
    - Raises RequestError if request failed
    - Raises ValueError if no `get_<name>` arguments were set to True
    """
    return __parse_html(**article_settings)

def articles_flow(
        amount: int, threads_amount: int = 10,
        buffer_size: int = 30, batch_size: int = 1,
        **article_settings
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
