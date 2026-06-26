from django import forms
from django.core.validators import RegexValidator
from django.forms import widgets
from common.common import get_random_code
from maneu.service import sendsms
class SendSMSForm(forms.Form):
    call = forms.CharField(
        label="手机号",
        required=True,
        strip=True,
        widget=widgets.TextInput(
            attrs={'id': 'call', 'class': 'form-control', 'placeholder': '请输入手机号'}
        ),
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '请输入正确的手机号格式')],
        error_messages={'required': '手机号不能为空'},
    )

    def clean(self):
        cleaned_data = super().clean()
        call = cleaned_data.get('call')
        try:
            # 生成6位随机验证码
            code = get_random_code()
            if sendsms(call, code) != 0:
                cleaned_data['code'] = code
                return cleaned_data
            else:
                raise forms.ValidationError('当前账号没注册')
        except Exception as e:
            raise forms.ValidationError(e)