from django.db import models
from django.contrib.auth.models import User

import os
import hashlib
import time

# Create your models here.
class UserExt(models.Model):
    user = models.OneToOneField(User)   #OneToOneField对已有的进行扩展
    realname = models.CharField("真实名称",max_length=64)
    birthday = models.DateField("生日")
    nickname = models.CharField("昵称",max_length=64)
    avatar = models.CharField("头像",max_length=256)   #avatar 头像
    telephone = models.CharField("移动电话",max_length=32)
    score = models.IntegerField("积分",default=0)
    logintime = models.DateTimeField("登陆时长",)
    validkey = models.CharField("验证码",max_length=256)
    status = models.IntegerField("状态",default=0)
    sex = models.IntegerField("性别",default=1)
    verification_time = models.IntegerField("失效时间",default=time.time() + 600)

    class Meta():
        verbose_name='用户信息'
        verbose_name_plural='用户信息'  #对于复数显示情况

    @classmethod
    def gen_validkey(cls):
        m=hashlib.md5()
        m.update(os.urandom(32))    #os.urandom 随机产生一个32位码
        return m.hexdigest()

    def __str__(self):
        return self.user.username

class UserAddress(models.Model):
    user=models.ForeignKey(User)    #ForeignKey 外键，一對多
    name = models.CharField("收货人",max_length=64)
    addr = models.CharField("收获地址",max_length=256)
    telephone = models.CharField("收货人电话",max_length=32)
    fixedphone = models.CharField("收货人固定电话",max_length=32)
    email = models.EmailField("收货人邮箱")
    status = models.IntegerField("收获地址状态",default=1)

    def __str__(self):
        return self.name    #用于显示地址时前边为收货人的名字


    class Meta():
        verbose_name='用户收获地址信息'
        verbose_name_plural='用户收获地址信息'  #对于复数显示情况




