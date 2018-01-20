# -*- coding: utf-8 -*-
# __author__ = "belic"
# __datetime__ = "2018/1/20 17:23"
import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == "__main__":
    print(get_md5("wwww.jobbole.com"))