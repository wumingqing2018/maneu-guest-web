"""
maneu/service.py

业务服务层：短信验证码 + 各业务对象的数据查询。
视图层只通过本模块访问数据库，不直接操作 Model。

约定：每个 get_* 函数自包含（filter + 排序 + 可选分页 + 字段裁剪），
     不通过公共函数委托，便于逐个独立修改。
"""

import random

from django.core.cache import cache
from django.forms.models import model_to_dict

from maneu.models import *


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
    """按手机号取 ORM 实例（生成 JWT 等需要属性访问的场景）。"""
    return ManeuGuest.objects.filter(phone=phone).first()


# ============================================================================
# 三、通用工具（供列表函数使用）
# ============================================================================

_LIST_FIELDS = ['id', 'name', 'time', 'phone', 'remark']


def _paginate(qs, offset=None, limit=None):
    """对 QuerySet 做可选切片；offset/limit 均为 None 时返回全量。"""
    if offset is not None and limit is not None:
        return qs[offset:offset + limit]
    if offset is not None:
        return qs[offset:]
    if limit is not None:
        return qs[:limit]
    return qs


# ============================================================================
# 四、列表查询（每个函数独立：filter + 排序 + 分页 + 字段裁剪）
# ============================================================================

def get_orders_by_phone(phone, offset=None, limit=None):
    """按手机号取订单列表（时间倒序）；可选 offset/limit 分页。"""
    qs = ManeuOrder.objects.filter(phone=phone).order_by('-time')
    qs = _paginate(qs, offset, limit)
    return list(qs.values(*_LIST_FIELDS))


def get_reports_by_phone(phone, offset=None, limit=None):
    """按手机号取报告列表（时间倒序）；可选 offset/limit 分页。"""
    qs = ManeuReport.objects.filter(phone=phone).order_by('-time')
    qs = _paginate(qs, offset, limit)
    return list(qs.values(*_LIST_FIELDS))


def get_stores_by_phone(phone, offset=None, limit=None):
    """按手机号取门店列表（时间倒序）；可选 offset/limit 分页。"""
    qs = ManeuStore.objects.filter(phone=phone).order_by('-time')
    qs = _paginate(qs, offset, limit)
    return list(qs.values(*_LIST_FIELDS))


def get_repairs_by_phone(phone, offset=None, limit=None):
    """按手机号取维修记录列表（时间倒序）；可选 offset/limit 分页。"""
    qs = ManeuRepair.objects.filter(phone=phone).order_by('-time')
    qs = _paginate(qs, offset, limit)
    return list(qs.values(*_LIST_FIELDS))


# ============================================================================
# 五、详情查询（每个函数独立：filter + first + model_to_dict）
# ============================================================================

# 机构对外公开的字段白名单。
# ⚠️ ManeuAdmin 实际字段：content / email / id / level / location /
#    nickname / password / phone / state / time / username
#    不含 remark；content 疑似授权 token，不放入白名单。
_ADMIN_PUBLIC_FIELDS = ('nickname', 'phone', 'location')


def get_admin_by_id(admin_id):
    """按 id 取机构公开信息；只查白名单字段，从 SQL 层裁剪敏感列。"""
    row = (
        ManeuAdmin.objects
        .filter(id=admin_id)
        .values(*_ADMIN_PUBLIC_FIELDS)
        .first()
    )
    return dict(row) if row else None


def get_order_by_id(record_id):
    """按 id 取订单详情。"""
    obj = ManeuOrder.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_report_by_id(record_id):
    """按 id 取报告详情。"""
    obj = ManeuReport.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_store_by_id(record_id):
    """按 id 取门店详情。"""
    obj = ManeuStore.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


def get_repair_by_id(record_id):
    """按 id 取维修记录详情。"""
    obj = ManeuRepair.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None