# 依赖包
import re


def order_id(string):
    try:
        pattern = r"^\d{10}$"
        if re.match(pattern, string, flags=0):
            return True
        return False
    except:
        return False


def token(string):
    try:
        pattern = r"^\d{64}$"
        if re.match(pattern, string, flags=0):
            return True
        return False
    except:
        return False
