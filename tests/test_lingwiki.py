from sys import path
path.append('../lingwiki')

from unittest import TestCase, main as testmain
from lingwiki import lingwiki as lw

class LingwikiTest(TestCase):
    def test_connection(self):
        self.assertIsInstance(lw.get_article(get_title=True)["title"], str)

if __name__ == '__main__':
    testmain()