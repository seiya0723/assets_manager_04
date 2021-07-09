from django import forms
from .models import Balance

class BalanceForm(forms.ModelForm):
    class Meta:
        model     = Balance
        #titleは無いので消す
        #fields   = [ "category","title","comment","income","spending","pay_dt"]
        fields   = [ "category","comment","income","spending","pay_dt"]


class YearForm(forms.Form):
    year     = forms.IntegerField()
