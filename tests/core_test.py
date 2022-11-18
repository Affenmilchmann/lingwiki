import os.path
from ssl import SSLEOFError, SSLError
from sys import path
from unittest import TestCase
from unittest import main as testmain
from parameterized import parameterized

from requests.exceptions import ConnectionError, ProxyError

path.append('../lingwiki')
from lingwiki import get_article, article_flow
from lingwiki._network import lang_codes

abs_path = os.path.abspath(os.path.dirname(__file__))

class ArticleFromURL(TestCase):
    longMessage = True
    data_path = os.path.join(abs_path, 'data\\')
    def article_test_template(self, url, result=-1, **kwargs):
        article = get_article(url, **kwargs)
        if result != -1:
            self.assertEqual(article, result)

    def test_base(self):
        self.article_test_template(
            url='https://en.wikipedia.org/wiki/Wikipedia',
            result={'title': 'Wikipedia'}
        )
        self.article_test_template(
            url='https://ru.wikipedia.org/wiki/Wikipedia',
            result={'title': 'Википедия'}
        )

    def test_all_lang_codes(self):
        return
        found = []
        notfound = []
        for i in range(len(lang_codes)):
            print(f"{i}/{len(lang_codes)}", end=" ")
            url = f'https://{lang_codes[i]}.wikipedia.org/wiki/Wikipedia'
            try:
                res = self.article_test_template(
                    url=url
                )
            except (TimeoutError, SSLError, ProxyError, ConnectionError):
                notfound.append(lang_codes[i])
                print(f"Failed to connect to '{url}'")
                continue
            found.append(lang_codes[i]) 
            print(f"Responded - '{url}'")
            with self.subTest():
                self.assertIsNone(res)
        print(f"Not found:\n {notfound}")
        print(f"{len(found)} found | {len(notfound)} not found.")

    def test_raise_invalid_url(self):
        with self.assertRaises(ValueError):
            self.article_test_template(
                url='https://eng.wikipedia.org/wiki/Wikipedia',
                ignore_invalid_urls=False
            )

    def test_dont_raise_invalid_url(self):
        try:
            self.article_test_template(
                url='https://eng.wikipedia.org/wiki/Wikipedia',
                ignore_invalid_urls=True
            )
        except ValueError as e:
            self.fail(f'get_article raised {e} in test_dont_raise_invalid_url')

    def test_blacklisted(self):
        self.article_test_template(
                url='https://en.wikipedia.org/wiki/Wikipedia',
                result=None,
                category_blacklist=['encyclopedia']
            )

    def test_not_blacklisted(self):
        self.article_test_template(
            url='https://en.wikipedia.org/wiki/Wikipedia',
            result={'title': 'Wikipedia'},
            category_blacklist=['human', 'city', 'science']
        )

if __name__ == "__main__":
    testmain()