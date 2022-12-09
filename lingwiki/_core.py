from ._threadpool import ThreadPool
from ._thread_targets import get_url_article_target
from ._defaults import WIKI_RAND_URL
from ._parse import parse_page
from ._network import get_html_file

def is_blacklisted(categories: list[str], blacklisted_categories: list[str]):
    if not categories: return True
    for cat in categories:
        for black_cat in blacklisted_categories:
            if black_cat.lower() in cat.lower():
                return True
    return False

def file_urls(file_name: str) -> str:
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

def list_urls(urls) -> str:
    for url in urls:
        yield url

def rand_urls(amount: int) -> str:
    for _ in range(amount):
        yield WIKI_RAND_URL

def __get_article(url, attempts=0, timeout=10, **kwargs) -> dict[str, str|dict|None]:
    if attempts < 0: return None
    keyword_args = {
        'ignore_invalid_urls': False,
        'category_blacklist': [],
        'categories': False,
        'get_url': False,
    }; keyword_args.update(kwargs)
    try:
        funal_url, page_html = get_html_file(
            url=url, 
            ignore_raise=keyword_args['ignore_invalid_urls'],
            timeout=timeout,
        )
    except TimeoutError as e:
        if attempts == 0:
            print(f"Max attempts reqched. Last exception: {e}")
            return None
        print(f"Timed out. Trying again in 15... ({attempts} attempts left)")
        return __get_article(url, attempts=attempts-1, **kwargs)

    if not page_html: 
        if not keyword_args['ignore_invalid_urls']:
            raise Exception(f"Got invalid html: {page_html}")
        else: return None
    
    page = parse_page(page_html, **kwargs)

    if is_blacklisted(page['categories'], keyword_args['category_blacklist']):
        return __get_article(url, attempts=attempts-1, **kwargs)
    if not keyword_args['categories']:
        del page['categories']
    if keyword_args['get_url']:
        page['get_url'] = funal_url
    return page

def get_article(url, timeout=10, **kwargs) -> dict:
    return __get_article(
        url,
        attempts_limit=0,
        timeout=timeout,
        **kwargs
    )

def article_flow(urls, thr_amount=10, batch_size=1, **kwargs):
    if urls == None: ValueError("'urls' kwarg must be provided")

    #print(f"{type(urls)} | {thr_amount} threads | {batch_size} batch size")

    if isinstance(urls, list) and sum([int(not isinstance(i, str)) for i in urls]) == 0:
        urls = list_urls(urls)
    elif isinstance(urls, str):
        urls = file_urls(urls)
    else: raise ValueError(f"'urls' must be file path string or list of strings")
    
    return 'it is not implemented'

def get_rand_article(lang, attempts_limit=5, timeout=10, **kwargs):
    # TODO
    pass

def rand_article_flow(thr_amount=10, buff_size=20, batch_size=1, timeout=5, **kwargs):
    keyword_args = {
        'lang': 'en',
    }
    pass
