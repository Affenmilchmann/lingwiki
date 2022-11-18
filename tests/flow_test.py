from sys import path
from time import sleep
from unittest import TestCase
from unittest import main as testmain
from parameterized import parameterized

import os
from sys import path
path.append('../lingwiki')

d_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/')
ru_file = d_name + 'ru_urls.txt'
with open(ru_file, 'r') as f: ru_file_len = len(f.readlines())
en_file = d_name + 'en_urls.txt'
with open(en_file, 'r') as f: en_file_len = len(f.readlines())
en_massive_file = d_name + 'en_massive.txt'
with open(en_massive_file, 'r') as f: en_massive_file_len = len(f.readlines())

array_test = [
    'list', 
    [
        'https://en.wikipedia.org/wiki/Musotima_instrumentalis',
        'https://en.wikipedia.org/wiki/Pierre_Capdevielle_(rugby_union)',
        'https://en.wikipedia.org/wiki/Cheiloceras',
        'https://en.wikipedia.org/wiki/Cinema_Audio_Society_Awards_2009',
        'https://en.wikipedia.org/wiki/Aleksandr_Osipov_(ice_hockey)',
    ],
    5
]

from lingwiki import article_flow

class TestFlow(TestCase):
    @parameterized.expand([
        array_test + [30],
        ['ru_file', ru_file, ru_file_len, 30],
        ['en_file', en_file, en_file_len, 30],
        array_test + [1],
        ['ru_file_1', ru_file, ru_file_len, 1],
        array_test + [2],
        #['ru_file_2', ru_file, ru_file_len, 2],
        #array_test + [5],
        #['ru_file_5', ru_file, ru_file_len, 5],
        #array_test + [15],
        #['ru_file_15', ru_file, ru_file_len, 15],
        #array_test + [50],
        #['ru_file_50', ru_file, ru_file_len, 50],
        #array_test + [200],
        #['ru_file_200', ru_file, ru_file_len, 200],
        ['massive', en_massive_file, en_massive_file_len, 300]
    ])
    def test_flow(self, name, inp, inp_len, thr_count):
        pass

if __name__ == "__main__":
    testmain()
