#encoding:utf-8

from django import forms
from .models import Category,Goods,Order

class GoodsAdminForm(forms.ModelForm):
    category=forms.ModelChoiceField(label='商品分类',queryset=Category.objects.filter(status=1)) #选择有的分类信息
    class Meta:
        model=Goods
        fields='__all__'

    def clean_price(self):
        price=self.cleaned_data.get('price',0)
        if price <=0:
            raise forms.ValidationError('价格必须要大于0')
        return price

    def clean_store(self):
        store=self.cleaned_data.get('store',0)
        if store <0:
            raise forms.ValidationError('库存不能小于0')
        return store

class OrderAdminForm(forms.ModelForm):
    status = forms.ChoiceField(widget=forms.Select, label="状态", choices=list(Order.STATUS_TEXTS.items()))

    class Meta:
        model = Order
        fields = '__all__'
