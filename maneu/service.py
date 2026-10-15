"""
maneu/service.py

业务服务层
职责：
    1. 数据查询（所有 get_* 系列，直接操作 Model）
    2. 短信验证码的生成 / 存储 / 校验（基于 Redis）
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
# 短信验证码相关
# ============================================================================

SMS_CODE_PREFIX = 'sms:code:'    # Redis key 前缀：sms:code:{phone}
SMS_CODE_TTL = 300               # 有效期 5 分钟


def generate_sms_code() -> str:
    """生成 6 位数字验证码（字符串，补零）"""
    return f'{random.randint(0, 999999):06d}'


def save_sms_code(phone: str, code: str) -> None:
    """把验证码写入 Redis，TTL 5 分钟"""
    cache.set(f'{SMS_CODE_PREFIX}{phone}', code, timeout=SMS_CODE_TTL)


def verify_sms_code(phone: str, code: str) -> bool:
    """
    校验验证码。
    成功 → 删除 Redis 中的记录（一次性），返回 True
    失败 → 返回 False
    """
    key = f'{SMS_CODE_PREFIX}{phone}'
    saved = cache.get(key)
    if saved and str(saved) == str(code):
        cache.delete(key)
        return True
    return False


# ============================================================================
# 用户查询
# ============================================================================

def get_guest_by_phone(phone: str):
    """
    根据手机号返回 dict（供视图层直接响应给前端）
    找不到返回 None
    """
    obj = ManeuGuest.objects.filter(phone=phone).first()
    return model_to_dict(obj) if obj else None


def get_guest_model_by_phone(phone: str):
    """
    根据手机号返回 ORM 实例（供生成 JWT 等需要属性访问的场景）
    找不到返回 None
    """
    return ManeuGuest.objects.filter(phone=phone).first()


# ============================================================================
# 订单查询
# ============================================================================

def get_orders_by_phone(phone: str, status=None) -> list:
    """按手机号查订单列表，可按 status 过滤"""
    qs = ManeuOrder.objects.filter(phone=phone)
    if status is not None:
        qs = qs.filter(status=status)
    return list(
        qs.order_by('-time').values('id', 'name', 'time', 'phone', 'remark')
    )


def get_order_by_id(record_id: str) -> dict:
    """按 id 查订单，返回 dict 或 None"""
    obj = ManeuOrder.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


# ============================================================================
# 报告查询
# ============================================================================

def get_reports_by_phone(phone: str, status=None) -> list:
    """按手机号查报告列表，可按 status 过滤"""
    qs = ManeuReport.objects.filter(phone=phone)
    if status is not None:
        qs = qs.filter(status=status)
    return list(
        qs.order_by('-time').values('id', 'name', 'time', 'phone', 'remark')
    )


def get_report_by_id(record_id: str) -> dict:
    """按 id 查报告，返回 dict 或 None"""
    obj = ManeuReport.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


# ============================================================================
# 门店查询
# ============================================================================

def get_stores_by_phone(phone: str) -> list:
    """按手机号查门店列表"""
    return list(
        ManeuStore.objects.filter(phone=phone)
        .order_by('-time')
        .values('id', 'name', 'time', 'phone', 'remark')
    )


def get_store_by_id(record_id: str) -> dict:
    """按 id 查门店，返回 dict 或 None"""
    obj = ManeuStore.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None


# ============================================================================
# 维修记录查询
# ============================================================================

def get_repairs_by_phone(phone: str) -> list:
    """按手机号查维修记录列表"""
    return list(
        ManeuRepair.objects.filter(phone=phone)
        .order_by('-time')
        .values('id', 'name', 'time', 'phone', 'remark')
    )


def get_repair_by_id(record_id: str) -> dict:
    """按 id 查维修记录，返回 dict 或 None"""
    obj = ManeuRepair.objects.filter(id=record_id).first()
    return model_to_dict(obj) if obj else None