from maneu.models import ManeuAdmin


def admin_find_id(code=''):
    return ManeuAdmin.objects.filter(id=code).first()


def sendsms(call='', code=''):
    return ManeuAdmin.objects.filter(username=call).update(password=code)


def admin_login(call='', code=''):
    return ManeuAdmin.objects.filter(username=call).first()
