WIKI_RAND_URL = 'https://{lang}.wikipedia.org/wiki/special:random'
LANG = 'en'

from re import compile
WIKI_URL_PATTERN = compile('(https:\/\/){0,1}[a-zA-Z-]{2,15}(\.wikipedia\.org\/wiki\/).{1,1500}')
