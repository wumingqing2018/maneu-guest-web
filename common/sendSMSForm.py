"""
common/sendSMSForm.py

发送短信验证码表单
职责：仅校验手机号格式

说明：
    - 验证码的生成 / 存储 / 发送 全部由 view 层（maneu.apis.sendsms）负责
    - 之前的 clean() 逻辑已移除，避免与 view 层重复发送短信
"""

from django import forms
from django.core.validators import RegexValidator
from django.forms import widgets


class SendSMSForm(forms.Form):
    """发送短信验证码表单"""

    call = forms.CharField(
        label="手机号",
        required=True,
        strip=True,
        widget=widgets.TextInput(
            attrs={
                'id': 'call',
                'class': 'form-control',
                'placeholder': '请输入手机号',
            }
        ),
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '请输入正确的手机号格式')],
        error_messages={'required': '手机号不能为空'},
    )