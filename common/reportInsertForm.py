"""
验光报告表单 (ManeuReport)
字段命名与前端提交一致，对应 ManeuReport 模型中的 od_*/os_* 字段。
所有字段均非必填，数值类型会进行格式校验，确保存入数据库的字符串合规。
"""
from django import forms
from decimal import Decimal, InvalidOperation


class ReportForm(forms.Form):
    # ========== 通用字段 ==========
    plan = forms.CharField(required=False, initial=None)
    pd = forms.CharField(required=False, initial=None)

    # ========== 右眼 (OD) ==========
    od_al = forms.CharField(required=False, initial=None)
    od_ak = forms.CharField(required=False, initial=None)
    od_ax = forms.DecimalField(required=False, initial=Decimal('0.00'))
    od_ad = forms.CharField(required=False, initial=None)
    od_add = forms.DecimalField(required=False, initial=Decimal('0.00'))
    od_bc = forms.CharField(required=False, initial=None)
    od_cyl = forms.DecimalField(required=False, initial=Decimal('0.00'))
    od_cct = forms.CharField(required=False, initial=None)
    od_va = forms.CharField(required=False, initial=None)
    od_sph = forms.DecimalField(required=False, initial=Decimal('0.00'))
    od_pr = forms.CharField(required=False, initial=None)
    od_fr = forms.CharField(required=False, initial=None)
    od_lt = forms.CharField(required=False, initial=None)
    od_vt = forms.CharField(required=False, initial=None)

    # ========== 左眼 (OS) ==========
    os_al = forms.CharField(required=False, initial=None)
    os_ak = forms.CharField(required=False, initial=None)
    os_ax = forms.DecimalField(required=False, initial=Decimal('0.00'))
    os_ad = forms.CharField(required=False, initial=None)
    os_add = forms.DecimalField(required=False, initial=Decimal('0.00'))
    os_bc = forms.CharField(required=False, initial=None)
    os_cyl = forms.DecimalField(required=False, initial=Decimal('0.00'))
    os_cct = forms.CharField(required=False, initial=None)
    os_va = forms.CharField(required=False, initial=None)
    os_sph = forms.DecimalField(required=False, initial=Decimal('0.00'))
    os_pr = forms.CharField(required=False, initial=None)
    os_fr = forms.CharField(required=False, initial=None)
    os_lt = forms.CharField(required=False, initial=None)
    os_vt = forms.CharField(required=False, initial=None)

    def clean(self):
        """
        可选的整体校验：
        - 确保数值字段存储为字符串（模型中是 CharField）
        - 将 None 值统一转为空字符串
        """
        cleaned_data = super().clean()
        for field_name, value in cleaned_data.items():
            if value is None:
                cleaned_data[field_name] = ''
            elif isinstance(value, Decimal):
                # 转为字符串保留两位小数
                cleaned_data[field_name] = f'{value:.2f}'
        return cleaned_data