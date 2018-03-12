#encoding: utf-8
from django.conf.urls import url
from . import views


app_name='account'
urlpatterns=[
    url(r'^register/',views.RegisterView.as_view(),name="register"),
    url(r'^active/',views.ActiveView.as_view(),name="active"),
    url(r'^login/', views.LoginView.as_view(), name="login"),
    url(r'^logout/', views.LogoutView.as_view(), name="logout"),
    url(r'^modify_password/', views.ModifyPasswordView.as_view(), name="modify_password"),
    url(r'^reset_password/', views.ResetPasswordView.as_view(), name="reset_password"),
    url(r'^reset_password_confirm/', views.ResetPasswordConfirmView.as_view(), name="reset_password_confirm"),
    url(r'^change_password/', views.ChangePasswordView.as_view(), name="change_password"),
    url(r'^test/',views.test, name="test"),
    url(r'^user_ext_base/',views.UserExtBaseView.as_view(), name="user_ext_base"),
    url(r'^user_ext_avatar/', views.UserExtAvatarView.as_view(), name="user_ext_avatar"),
    url(r'^user_address/$', views.UserAddressListView.as_view(), name="user_address"),
    url(r'^user_address_create/$', views.UserAddressCreateView.as_view(), name="user_address_create"),
    url(r'^test_args_kwargs/(?P<a>\d+)/(?P<b>\d+)/$',views.test_args_kwargs.as_view(), name="test_args_kwargs"),
    #正则 d:0-9, d+:最少有一个0-9的数字, \d+存于args形成的元组中, ?P<a>d+ 命名该数据为a,P大写，存于kwargs形成的字典中.
    # (\d+)/(\d+)/与(?P<a>\d+)/(?P<b>\d+)/不能在一起写，否着只显示kwargs的
    url(r'^user_address_delete/(?P<pk>\d+)/$', views.UserAddressDeleteView.as_view(), name="user_address_delete"),
    url(r'^user_address_update/(?P<pk>\d+)/$', views.UserAddressUpdateView.as_view(), name="user_address_update"),

]

