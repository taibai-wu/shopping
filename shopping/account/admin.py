from django.contrib import admin

from .models import UserExt,UserAddress
# Register your models here.
admin.site.register(UserExt)
admin.site.register(UserAddress)