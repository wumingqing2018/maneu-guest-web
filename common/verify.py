import re

def is_call(code):
    pattern = re.compile(r'^1[3-9]\d{9}$')
    if pattern.match(code) is not None:
        return str(code)
    else:
        return None


def is_code(code):
    pattern = re.compile(r'^\d{6}$')
    if pattern.match(code) is not None:
        return str(code)
    else:
        return None


def is_uuid(code):
    pattern = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    if pattern.match(code) is not None:
        return str(code)
    else:
        return None