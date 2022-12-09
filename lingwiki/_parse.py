from bs4 import BeautifulSoup

def parse_page(html, **kwargs):
    keyword_args = {
        'title': True,
        'paragraphs': False,
        'images': False,
        'links': False,
    }
    keyword_args.update(kwargs)
    soup = BeautifulSoup(html, 'html.parser')
    return_dict = {} 

    try: 
        return_dict['categories'] = [p.get_text() for p in soup.find(id = 'mw-normal-catlinks').find_all('li')]
    except AttributeError: return_dict['categories'] = None
    try: 
        if keyword_args['title']: return_dict['title'] = soup.find(id="firstHeading").get_text()
    except AttributeError: return_dict['title'] = None
    try:
        if keyword_args['paragraphs']: return_dict['paragraphs'] = [p.get_text() for p in soup.find_all('p')]
    except AttributeError: return_dict['paragraphs'] = None
    try:
        if keyword_args['images']: return_dict['images'] = [raw_img['src'] for raw_img in soup.find_all('img')]
    except AttributeError: return_dict['images'] = None

    return return_dict
