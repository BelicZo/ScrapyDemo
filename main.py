# -*- coding: utf-8 -*-
# __author__ = "belic"
# __datetime__ = "2018/1/18 21:12"
import sys
import os

from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(['scrapy', 'crawl', '--loglevel=WARN', 'jobbole'])
