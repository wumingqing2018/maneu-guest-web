"""
maneu/service.py

业务服务层
封装所有数据访问与业务逻辑，供 apis.py 等视图层调用。

职责：
    1. 短信验证码的生成 / 存储 / 校验（基于 Redis）
    2. 用户、订单、报告、门店、维修记录的数据查询

约定：
    - get_*_by_id              返回 dict 或 None（供详情接口）
    - get_*_by_phone           返回 list[dict]（供列表接口）
    - get_guest_by_phone       返回 dict 或 None（已排除 password 字段）
    - get_guest_model_by_phone 返回 ORM 实例或 None（供生成 JWT 等场景）
"""

import random

from django.core.cache import cache
from django.forms.models import model_to_dict

from maneu.models import (
    ManeuGuest,
    ManeuOrder,
    ManeuReport,
    ManeuStore,
    ManeuRepair,
)


# ============================================================================
# 一、短信验证码
# ============================================================================

SMS_CODE_PREFIX = 'sms:code:'    # Redis key 前缀：sms:code:{phone}
SMS_CODE_TTL = 300               # 有效期（秒）


def generate_sms_code():
    """
    生成 6 位数字验证码（字符串，补零）。

    :return: 6 位数字字符串，如 '012345'
    :rtype: str
    :example:
        >>> generate_sms_code()
        '048271'
    """
    return f'{random.randint(0, 999999):06d}'


def save_sms_code(phone, code):
    """
    将验证码写入 Redis，5 分钟后自动过期。

    :param phone: 手机号
    :type phone: str
    :param code: 6 位验证码
    :type code: str
    """
    cache.set(f'{SMS_CODE_PREFIX}{phone}', code, timeout=SMS_CODE_TTL)


def verify_sms_code(phone, code):
    """
    校验验证码。

    - 校验成功：从 Redis 中删除该 key（一次性使用），返回 True
    - 校验失败或已过期：返回 False

    :param phone: 手机号
    :type phone: str
    :param code: 待校验的 6 位验证码
    :type code: str
    :return: 校验是否通过
    :rtype: bool
    """
    key = f'{SMS_CODE_PREFIX}{phone}'
    saved = cache.get(key)

    if saved is None:
        return False

    if str(saved) != str(code):
        return False

    cache.delete(key)
    return True


# ============================================================================
# 二、用户查询
# ============================================================================

def get_guest_by_phone(phone):
    """
    按手机号查用户，返回 dict（供视图层直接响应给前端）。

    ⚠️ 主动排除 password 字段，避免密码哈希泄露。

    :param phone: 手机号
    :type phone: str
    :return: 用户信息 dict，找不到返回 None
    :rtype: dict or None
    """
    obj = ManeuGuest.objects.filter(phone=phone).first()
    if not obj:
        return None

    data = model_to_dict(obj)
    data.pop('password', None)
    return data


def get_guest_model_by_phone(phone):
    """
    按手机号查用户，返回 ORM 实例。

    用于需要访问属性（如 user.id / user.phone）的场景，例如生成 JWT。

    :param phone: 手机号
    :type phone: str
    :return: ManeuGuest 实例，找不到返回 None
    :rtype: ManeuGuest or None
    """
    return ManeuGuest.objects.filter(phone=phone).first()


# ============================================================================
# 三、列表查询（按手机号）
# ============================================================================

# 列表接口统一返回的字段（订单 / 报告 / 门店 / 维修 共用）
_LIST_FIELDS = ['id', 'name', 'time', 'phone', 'remark']


def get_orders_by_phone(phone, status=None):
    """
    按手机号查订单列表。

    :param phone: 手机号
    :type phone: str
    :param status: 订单状态过滤，None 表示不过滤
    :type status: int or None
    :return: 订单列表（仅含 _LIST_FIELDS 定义的字段）
    :rtype: list[dict]
    """
    qs = ManeuOrder.objects.filter(phone=phone)
    if status is not None:
        qs = qs.filter(status=status)
    return list(qs.order_by('-time').values(*_LIST_FIELDS))


def get_reports_by_phone(phone, status=None):
    """
    按手机号查报告列表。

    :param phone: 手机号
    :type phone: str
    :param status: 报告状态过滤，None 表示不过滤
    :type status: int or None
    :return: 报告列表（仅含 _LIST_FIELDS 定义的字段）
    :rtype: list[dict]
    """
    qs = ManeuReport.objects.filter(phone=phone)
    if status is not None:
        qs = qs.filter(status=status)
    return list(qs.order_by('-time').values(*_LIST_FIELDS))


def get_stores_by_phone(phone):
    """
    按手机号查门店列表。

    :param phone: 手机号
    :type phone: str
    :return: 门店列表（仅含 _LIST_FIELDS 定义的字段）
    :rtype: list[dict]
    """
    qs = ManeuStore.objects.filter(phone=phone).order_by('-time')
    return list(qs.values(*_LIST_FIELDS))


def get_repairs_by_phone(phone):
    """
    按手机号查维修记录列表。

    :param phone: 手机号
    :type phone: str
    :return: 维修记录列表（仅含 _LIST_FIELDS 定义的字段）
    :rtype: list[dict]
    """
    qs = ManeuRepair.objects.filter(phone=phone).order_by('-time')
    return list(qs.values(*_LIST_FIELDS))


# ============================================================================
# 四、详情查询（按 ID）
# ============================================================================

def get_order_by_id(record_id):
    """
    按 id 查订单详情。

    :param record_id: 订单 UUID
    :type record_id: str
    :return: 订单 dict，找不到返回 None
    :rtype: dict or None
    """
    obj = ManeuOrder.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_report_by_id(record_id):
    """
    按 id 查报告详情。

    :param record_id: 报告 UUID
    :type record_id: str
    :return: 报告 dict，找不到返回 None
    :rtype: dict or None
    """
    obj = ManeuReport.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_store_by_id(record_id):
    """
    按 id 查门店详情。

    :param record_id: 门店 UUID
    :type record_id: str
    :return: 门店 dict，找不到返回 None
    :rtype: dict or None
    """
    obj = ManeuStore.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_repair_by_id(record_id):
    """
    按 id 查维修记录详情。

    :param record_id: 维修记录 UUID
    :type record_id: str
    :return: 维修记录 dict，找不到返回 None
    :rtype: dict or None
    """
    obj = ManeuRepair.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None