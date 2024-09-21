from django import forms
from django.core.validators import RegexValidator
from django.forms import widgets
from maneu.models import ManeuGuess



class UserLoginForm(forms.Form):
    call = forms.CharField(label="手机号",
                           required=True,
                           strip=True,
                           widget=widgets.TextInput(
                               attrs={'id': 'call', 'class': 'form-control', 'placeholder': '手机号'}
                           ),
                           validators=[
                               RegexValidator(r'^1[3-9]\d{9}$', '请输入正确的手机号')
                           ],
                           error_messages={'required': '请输入手机号'},
                           )
    code = forms.CharField(label="验证码",
                           required=True,
                           strip=True,
                           widget=widgets.PasswordInput(
                               attrs={'id': 'code', 'class': 'form-control', 'placeholder': '验证码'}
                           ),
                           validators=[
                               RegexValidator(r'^\d{6}$', '请输入正确的验证码')
                           ],
                           error_messages={'required': '请输入验证码'},
                           )

    def clean(self):
        call = self.cleaned_data.get('call')
        code = self.cleaned_data.get('code')
        verify = ManeuGuess.objects.filter(phone=call, remark=code).first()
        if verify:
            raise forms.ValidationError('登录失败，账号还是密码错误，请确认账号和密码')
