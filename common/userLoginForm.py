"""
common/userLoginForm.py

短信验证码登录表单
职责：
    1. 校验手机号格式
    2. 校验验证码（从 Redis 取，成功后删除）
    3. 从数据库拿 ManeuGuest 实例，放入 cleaned_data['user']

字段：
    call - 手机号
    code - 6 位数字验证码
"""

from django import forms
from django.core.validators import RegexValidator

from maneu.models import ManeuGuest
from maneu.service import verify_sms_code


class UserLoginForm(forms.Form):
    """短信验证码登录表单"""

    call = forms.CharField(
        label="手机号",
        required=True,
        strip=True,
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '请输入正确的手机号格式')],
        error_messages={'required': '手机号不能为空'},
    )

    code = forms.CharField(
        label="验证码",
        required=True,
        strip=True,
        validators=[RegexValidator(r'^\d{6}$', '验证码必须是 6 位数字')],
        error_messages={'required': '验证码不能为空'},
    )

    def clean(self):
        cleaned_data = super().clean()
        call = cleaned_data.get('call')
        code = cleaned_data.get('code')

        # 前置校验失败时直接返回，避免后面报错
        if not call or not code:
            return cleaned_data

        # 1. 校验验证码（成功后 Redis 里删除）
        if not verify_sms_code(call, code):
            raise forms.ValidationError('验证码错误或已过期')

        # 2. 查用户（必须是 ORM 实例，供后续生成 JWT 用）
        user = ManeuGuest.objects.filter(phone=call).first()
        if not user:
            raise forms.ValidationError('该手机号未注册')

        # 3. 挂到 cleaned_data，视图层会读这个
        cleaned_data['user'] = user
        return cleaned_data