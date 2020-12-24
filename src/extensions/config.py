# -*- coding: utf-8 -*-
"""doc string"""

import os as _os
from configparser import ConfigParser as _ConfigParser

config = _ConfigParser()
config.read(_os.path.join(
    _os.path.dirname(__file__),
    r'..\..\config.ini',
))


if __name__ == '__main__':
    print(config.get('account', 'username'))
