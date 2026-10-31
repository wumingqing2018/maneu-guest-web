"""
maneu/service.py

业务服务层：短信验证码 + 各业务对象的数据查询。
视图层只通过本模块访问数据库，不直接操作 Model。
"""

import random

from django.core.cache import cache
from django.forms.models import model_to_dict

from maneu.models import (
    ManeuAdmin, ManeuGuest, ManeuOrder, ManeuReport, ManeuStore, ManeuRepair,
)


# ============================================================================
# 一、短信验证码
# ============================================================================

SMS_CODE_PREFIX = 'sms:code:'   # Redis key：sms:code:{phone}
SMS_FAIL_PREFIX = 'sms:fail:'   # Redis key：sms:fail:{phone}
SMS_CODE_TTL = 300              # 验证码有效期（秒）
SMS_FAIL_LIMIT = 5              # 连续错误上限，达到后作废验证码


def generate_sms_code():
    """生成 6 位数字验证码，左补零（如 '048271'）。"""
    return f'{random.randint(0, 999999):06d}'


def save_sms_code(phone, code):
    """写入验证码（5 分钟过期），并重置该手机号的错误计数。"""
    cache.set(f'{SMS_CODE_PREFIX}{phone}', code, timeout=SMS_CODE_TTL)
    cache.delete(f'{SMS_FAIL_PREFIX}{phone}')


def verify_sms_code(phone, code):
    """校验验证码；成功即从 Redis 删除（一次性使用）。"""
    key = f'{SMS_CODE_PREFIX}{phone}'
    saved = cache.get(key)
    if saved is None or str(saved) != str(code):
        return False
    cache.delete(key)
    return True


def is_sms_locked(phone):
    """是否因错误次数达到上限而被锁定。"""
    return cache.get(f'{SMS_FAIL_PREFIX}{phone}', 0) >= SMS_FAIL_LIMIT


def record_sms_fail(phone):
    """记录一次错误；达到上限时作废验证码，强制重新获取。"""
    key = f'{SMS_FAIL_PREFIX}{phone}'
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=SMS_CODE_TTL)
    if count >= SMS_FAIL_LIMIT:
        cache.delete(f'{SMS_CODE_PREFIX}{phone}')


# ============================================================================
# 二、用户查询
# ============================================================================

def get_guest_by_phone(phone):
    """按手机号取用户 dict（视图层响应使用）；已剔除 password。"""
    obj = ManeuGuest.objects.filter(phone=phone).first()
    if not obj:
        return None
    data = model_to_dict(obj)
    data.pop('password', None)
    return data


def get_guest_model_by_phone(phone):
    """按手机号取 ORM 实例（生成 JWT 等需要属性访问的场景）。"""
    return ManeuGuest.objects.filter(phone=phone).first()


# ============================================================================
# 三、列表查询（按手机号）
# ============================================================================

_LIST_FIELDS = ['id', 'name', 'time', 'phone', 'remark']


def _paginate(qs, offset=None, limit=None):
    """可选切片；offset/limit 均为 None 时返回全量。"""
    if offset is not None and limit is not None:
        return qs[offset:offset + limit]
    if offset is not None:
        return qs[offset:]
    if limit is not None:
        return qs[:limit]
    return qs


def _list_by_phone(model, phone, offset=None, limit=None):
    """按手机号取列表（时间倒序），只返回 _LIST_FIELDS。"""
    qs = model.objects.filter(phone=phone).order_by('-time')
    return list(_paginate(qs, offset, limit).values(*_LIST_FIELDS))


def get_orders_by_phone(phone, offset=None, limit=None):
    return _list_by_phone(ManeuOrder, phone, offset, limit)


def get_reports_by_phone(phone, offset=None, limit=None):
    return _list_by_phone(ManeuReport, phone, offset, limit)


def get_stores_by_phone(phone, offset=None, limit=None):
    return _list_by_phone(ManeuStore, phone, offset, limit)


def get_repairs_by_phone(phone, offset=None, limit=None):
    return _list_by_phone(ManeuRepair, phone, offset, limit)


# ============================================================================
# 四、详情查询（按 ID）
# ============================================================================

# 机构对外公开的字段。显式白名单，防止 password / 授权 token 等泄露。
# 目前模型字段名与响应键名一致；若日后需重命名，改为 {模型字段: 响应键} 字典。
_ADMIN_PUBLIC_FIELDS = ('nickname', 'phone', 'location', 'remark')


def get_admin_by_id(admin_id):
    """按 id 取机构公开信息；只查白名单字段，从 SQL 层裁剪敏感列。"""
    row = (
        ManeuAdmin.objects
        .filter(id=admin_id)
        .values(*_ADMIN_PUBLIC_FIELDS)
        .first()
    )
    return dict(row) if row else None


def _get_by_id(model, record_id):
    obj = model.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_order_by_id(record_id):
    return _get_by_id(ManeuOrder, record_id)


def get_report_by_id(record_id):
    return _get_by_id(ManeuReport, record_id)


def get_store_by_id(record_id):
    return _get_by_id(ManeuStore, record_id)


def get_repair_by_id(record_id):
    return _get_by_id(ManeuRepair, record_id)