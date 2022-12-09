from ._defaults import LANG, WIKI_RAND_URL, WIKI_URL_PATTERN
def form_url(url=None, lang=None) -> str:
    if url: return url
    return WIKI_RAND_URL.format(lang if lang else LANG)

def check_urls_format(urls: list[str]):
    pass

def is_blacklisted(categories: list[str], blacklisted_categories: list[str]):
    for cat in categories:
        for black_cat in blacklisted_categories:
            if black_cat.lower() in cat.lower():
                return True
    return False
