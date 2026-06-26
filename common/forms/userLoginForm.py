from django import forms
from django.core.validators import RegexValidator
from django.forms import widgets

from maneu.service import admin_login


class UserLoginForm(forms.Form):
    call = forms.CharField(label="手机",
                           required=True,
                           strip=True,
                           widget=widgets.TextInput(
                               attrs={'id': 'call', 'class': 'form-control', 'placeholder': '账号'}
                           ),
                           validators=[RegexValidator(r'^1[3-9]\d{9}$', '请输入正确的账号')],
                           error_messages={'required': '请输入账号'},
                           )
    code = forms.CharField(label="短信",
                           required=True,
                           strip=True,
                           widget=widgets.PasswordInput(
                               attrs={'id': 'code', 'class': 'form-control', 'placeholder': '密码'}
                           ),
                           validators=[RegexValidator(r'^\d{6}$', '请输入正确的验证码')],
                           error_messages={'required': '请输入验证码'},
                           )

    def clean(self):
        cleaned_data = super().clean()
        call = self.cleaned_data.get('call')
        code = self.cleaned_data.get('code')
        # 自定义验证：查询用户对象并存入 cleaned_data
        try:
            user = admin_login(call, code)
            # 如果密码也正确，才将 user 存入（此处只做示例）
            if user is not None:
                cleaned_data['user'] = user          # 添加自定义键
                return cleaned_data
            else:
                raise forms.ValidationError('验证码错误')

        except Exception as e:
            raise forms.ValidationError(e)
