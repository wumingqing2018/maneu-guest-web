# https://code.ziqiangxuetang.com/django/django-deploy.html
import os
import sys  # 4

from os.path import join
from os.path import dirname
from os.path import abspath
from django.core.wsgi import get_wsgi_application

PROJECT_DIR = dirname(dirname(abspath(__file__)))  # 3
sys.path.insert(0, PROJECT_DIR)  # 5

os.environ["DJANGO_SETTINGS_MODULE"] = "maneu_guest.settings"  # 7

application = get_wsgi_application()
