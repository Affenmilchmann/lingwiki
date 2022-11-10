from bs4 import BeautifulSoup
from typing import TextIO

from utils import get_html_file, is_blacklisted, form_url

def __get_article(url=None, lang=None, attempts_limit=0, timeout=10, **kwargs) -> dict[str, str|dict|None]:
    if attempts_limit < 0: return None
    keyword_args = {
        'title': True,
        'paragraphs': False,
        'categories': False,
        'images': False,
        'links': False,
        'category_blacklist': []
    }
    keyword_args.update(kwargs)

    soup = BeautifulSoup(
                get_html_file(
                    timeout=timeout, 
                    url = form_url(url, lang),
                ),
                'html.parser'
        )
    categories = [p.get_text() for p in soup.find(id = 'mw-normal-catlinks').find_all('li')]
    if not url and is_blacklisted(categories, keyword_args['category_blacklist']): 
        return __get_article(
                url,
                attempts_limit=attempts_limit-1,
                timeout=timeout,
                **kwargs
            )

    return_dict = {}

    if keyword_args['title']: return_dict['title'] = soup.find(id="firstHeading").get_text()
    if keyword_args['paragraphs']: return_dict['paragraphs'] = [p.get_text() for p in soup.find_all('p')]
    if keyword_args['categorits']: return_dict['categorits'] = categories
    if keyword_args['images']: return_dict['images'] = [raw_img['src'] for raw_img in soup.find_all('img')]
    # TODO if article_content['title']: 

    return return_dict

def get_article(url, attempts_limit=5, timeout=10, **kwargs):
    return __get_article(
            url=url, 
            attempts_limit=attempts_limit,
            timeout=timeout,
            **kwargs
        )

def article_flow(thr_amount=10, buff_size=20, batch_size=1, timeout=5, **kwargs):
    keyword_args = {
        'urls': None,  # list[str] | str (file path) | filestream
    }
    keyword_args.update(kwargs)
    if keyword_args['urls'] == None: ValueError("'urls' kwarg must be provided")

    url_list: list[str]
    
    if isinstance(keyword_args['urls'], list):
        if len(keyword_args['urls']) < 2: 
            raise ValueError("'urls' list must contain at least 2 links")
        if sum([int(not isinstance(url, str)) for url in keyword_args['urls']]) != 0: 
            raise ValueError("'urls' list must contain strings only")
        url_list = keyword_args['urls']
    if isinstance(keyword_args['urls'], str):
        pass
    if isinstance(keyword_args['urls'], TextIO):
        pass
    

def get_rand_article(lang, attempts_limit=5, timeout=10, **kwargs):
    keyword_args = {
        'categ_blacklist': []
    }
    keyword_args.update(kwargs)
    # TODO
    pass

def rand_article_flow(thr_amount=10, buff_size=20, batch_size=1, timeout=5, **kwargs):
    keyword_args = {
        'lang': 'en',
    }
    pass
