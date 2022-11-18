from requests import get as req_get
import os.path

from ._defaults import WIKI_URL_PATTERN

lang_codes_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/wiki_lang_codes.txt')
lang_codes = []
with open(lang_codes_file, 'r', encoding='utf-8') as f:
    lang_codes = [l.strip() for l in f.readlines()]

def check_lang(url: str):
    lang = url.replace('https://', '').replace('http://', '').replace('www.', '')
    lang = lang.split('.', 1)[0]
    return lang in lang_codes

def validate_url(url, ignore_raise):
    if bool(WIKI_URL_PATTERN.fullmatch(url)) and check_lang(url): return True
    # if do_log: pass  TODO logging
    if not ignore_raise: raise ValueError(f"'{url}' is not a valid wikipedia url.")
    return False

def get_html_file(timeout=10, url=None, ignore_raise=False):
    if not validate_url(url, ignore_raise=ignore_raise): return url, None
    headers = {'Accept-Encoding': 'identity'}
    r = req_get(url, headers=headers, timeout=timeout)
    return r.url, r.text
