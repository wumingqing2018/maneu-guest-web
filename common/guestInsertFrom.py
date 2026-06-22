import re
from datetime import datetime
from django import forms



class GuestInsertFrom(forms.Form):
    """
    客户新增表单
    - time:  时间字段，支持 "YYYY-MM-DD HH:MM:SS" 或 "YYYY-MM-DD"，未填默认当前时间
    - name:  字符串，可选
    - phone: 手机号，可选但若填写需符合格式
    - remark: 字符串，可选（对应前端 guestRemark）
    - age, sex, ot, em, dfh: 字符串，可选
    """
    time = forms.CharField(
        required=False,
        help_text="格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS，未填默认为当前时间"
    )
    name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    guestRemark = forms.CharField(required=False)  # 前端字段名
    age = forms.CharField(required=False)
    sex = forms.CharField(required=False)
    ot = forms.CharField(required=False)
    em = forms.CharField(required=False)
    dfh = forms.CharField(required=False)

    def clean_time(self):
        """解析并校验时间字段，若为空则返回当前时间"""
        time_str = self.cleaned_data.get('time')
        if not time_str:
            return datetime.now()

        # 尝试两种格式解析
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        raise forms.ValidationError("时间格式错误，需为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")

    def clean_phone(self):
        """手机号校验：若填写了则必须符合格式"""
        phone = self.cleaned_data.get('phone')
        if phone:
            if not re.match(r'^1[3-9]\d{9}$', phone):
                raise forms.ValidationError("手机号格式不正确")
        return phone

    def clean(self):
        """可选的整体校验"""
        cleaned_data = super().clean()
        # 若需额外逻辑（如 name 和 phone 不能同时为空），可在此添加
        return cleaned_data
