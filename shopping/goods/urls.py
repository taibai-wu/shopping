#encoding: utf-8
from django.conf.urls import url

from . import views  # 从当前目录下倒入
app_name='goods'
urlpatterns=[
    url(r'^$',views.GoodsListView.as_view(),name='goods'),
    url(r'^(?P<pk>\d+)/$', views.GoodsDetailView.as_view(), name="goods_detail"),
    url(r'^add_shopping_car/$',views.ShoppingCarCreateView.as_view(),name='add_shopping_car'),
    url(r'^get_shopping_car_num/$',views.ShoppingCarNumView.as_view(),name='get_shopping_car_num'),
    url(r'^shopping_car/$',views.ShoppingCarView.as_view(),name='shopping_car'),
    url(r'^remove_shopping_car/$', views.ShoppingCarDeleteView.as_view(), name='remove_shopping_car'),
    url(r'^create_order/$', views.OrderCreateView.as_view(), name="create_order"),
    url(r'^orders/$', views.OrderListView.as_view(), name="orders"),
    url(r'^order_operate/$', views.OrderOperateView.as_view(), name="order_operate"),
]
