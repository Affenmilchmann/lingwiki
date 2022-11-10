from requests import get as req_get
from typing import TextIO

from defaults import DEFAULT_LANG, DEFAULT_WIKI_URL

def get_html_file(timeout=10, url=None):
    headers = {'Accept-Encoding': 'identity'}
    r = req_get(url, headers=headers, timeout=timeout)
    return r.text

def is_blacklisted(categories: list[str], blacklisted_categories: list[str]):
    for cat in categories:
        for black_cat in blacklisted_categories:
            if black_cat in cat:
                return True
    return False

def form_url(url=None, lang=None) -> str:
    url = url if url else DEFAULT_WIKI_URL
    return url.format(lang = lang if lang else DEFAULT_LANG)

def load_urls_from_text_stream(text_stream: TextIO) -> list[str]:
    if not isinstance(text_stream, TextIO): raise ValueError('IO must be text stream (TextIO)')
    text_stream.readlines()

def load_urld_from_file(file_name: str) -> list[str]:
    with open(file_name, 'r', encoding='utf-8') as f:
        return load_urls_from_text_stream(f)

def check_urls_format(urls: list[str]):
    pass
