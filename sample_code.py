# -*- coding: utf-8 -*-
"""doc string"""

from src import download_user


def main():
    res = download_user(
        12345678,
        image_type='ugoira,illust,manga',
        file_name_rule=None,
        dst_dir_rule=r'download\{user.name}',
        size='original',
        replace=False,
        download_mode='thread',
    )
    print(res)


if __name__ == '__main__':
    main()
