from maneu.models import ManeuOrderV2


def ManeuOrderV2_phone(code):
    return ManeuOrderV2.objects.filter(phone=code).all()