# -*- coding: utf-8 -*-
"""doc string"""

from enum import Enum as _Enum, unique as _unique


@_unique
class ErrorCode(_Enum):
    LoginError = 1000
    UserNotFound = 2000
    ImageNotFound = 3000
    InvalidImageSize = 3001
    MissingArgument = 4000
    ImageUrlNotSupported = 5000
    ImageTypeNotSupported = 5001


class PixivFetcherError(Exception):

    def __init__(self, err_code, err_msg=None):
        self.code = err_code
        self.msg = err_msg
        super().__init__(self.get_msg())

    def get_msg(self):
        pre = f'[ErrorCode {self.code.value}] {self.code.name}'
        suf = f': {self.msg}' if self.msg else ''
        return f'{pre}{suf}'


if __name__ == '__main__':
    pass
