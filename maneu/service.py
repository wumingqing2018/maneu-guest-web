from django.forms.models import model_to_dict

from maneu.models import ManeuGuest, ManeuOrder, ManeuReport, ManeuStore, ManeuRepair


def get_guest_by_phone(phone: str):
    """根据手机号返回 ManeuGuest 实例或 None"""
    try:
        return ManeuGuest.objects.get(phone=phone)
    except ManeuGuest.DoesNotExist:
        return None


def get_orders_by_phone(phone: str, status=None) -> list:
    qs = ManeuOrder.objects.filter(phone=phone)
    if status is not None:
        qs = qs.filter(status=status)
    return list(qs.order_by('-time').values('id', 'name', 'time', 'phone', 'remark'))


def get_reports_by_phone(phone: str, status=None) -> list:
    qs = ManeuReport.objects.filter(phone=phone)
    if status is not None:
        qs = qs.filter(status=status)
    return list(qs.order_by('-time').values('id', 'name', 'time', 'phone', 'remark'))


def get_stores_by_phone(phone: str) -> list:
    return list(ManeuStore.objects.filter(phone=phone).order_by('-time').values('id', 'name', 'time', 'phone', 'remark'))


def get_repairs_by_phone(phone: str) -> list:
    return list(ManeuRepair.objects.filter(phone=phone).order_by('-time').values('id', 'name', 'time', 'phone', 'remark'))


def get_order_by_id(record_id: str) -> dict:
    obj = ManeuOrder.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_store_by_id(record_id: str) -> dict:
    obj = ManeuStore.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_report_by_id(record_id: str) -> dict:
    obj = ManeuReport.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_repair_by_id(record_id: str) -> dict:
    obj = ManeuRepair.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_guest_by_phone(phone: str):
    obj = ManeuGuest.objects.filter(phone=phone).first()
    return model_to_dict(obj) if obj else None