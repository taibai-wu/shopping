import datetime
import json
import time
import os

from django.conf import settings
from django.utils import timezone
from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import render
from django.views.generic import View, FormView,ListView,CreateView,DeleteView,UpdateView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect,Http404
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse,reverse_lazy    #导入url tag
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.db import transaction
from django.contrib import messages     #django自身message模块，实现类似session的功能

from .decorator import login_required,timing
from .models import UserExt,UserAddress
from .forms import RegisterForm, LoginForm, ResetPasswordForm,ResetPasswordConfirmForm,\
    ChangePasswordForm,UserExtBaseForm,UserExtAvatarForm,UserAddressForm

from django.utils.decorators import method_decorator
from .mixins import LoginRequiredMixin,ObjectPermMixin

class RegisterView(View):      #注册用户

    def post(self,request,*args,**kwargs):
        form = RegisterForm(request.POST)
        return self._register(form)


    def _register(self,form):
        if form.is_valid():
            username = form.cleaned_data.get('username', '')
            password = form.cleaned_data.get('password', '')
            email = form.cleaned_data.get('email', '')
            try:
                with transaction.atomic():
                    user = User.objects.create_user(username=username, password=password, email=email)
                    validkey = UserExt.gen_validkey()

                    user_ext = UserExt.objects.create(user=user, realname='', birthday=datetime.date(1945, 1, 1), \
                                                      nickname=username, avatar='default', telephone='', \
                                                      logintime=timezone.now(), validkey=validkey)

                    content = '欢迎注册商城帐号, 请点击此处进行激活用户: http://192.168.3.8:8888/account/active/?username={username}&validkey={validkey}'.format(
                        username=username, validkey=validkey)
                    send_mail('用户注册', content, settings.EMAIL_HOST_USER, [email])
            except BaseException as e:
                print(e)
                return JsonResponse({'status': 500, 'errors': ['服务器错误']})
            return JsonResponse({'status': 200})
        else:
            return JsonResponse({'status': 400, 'errors': json.loads(form.errors.as_json()), 'result': ''})


    def get(self,request,*args,**kwargs):
        form = RegisterForm(request.GET)
        return self._register(form)


class ActiveView(View):     #验证注册

    def get(self,request,*args,**kwargs):
        username = request.GET.get('username', '')
        validkey = request.GET.get('validkey', '')
        try:
            user=User.objects.get(username=username)
            if user.userext.validkey==validkey:
                if user.userext.status==0 and user.userext.validkey !='':
                    user.userext.status = 1
                    user.userext.validkey=''
                    if time.time()<user.userext.verification_time:
                        user.userext.save()
                        messages.add_message(request,messages.INFO,"激活成功，请登陆")
                        return HttpResponseRedirect(reverse('index'))
                    else:
                        messages.add_message(request, messages.ERROR, "激活失败，验证超时")
                        return HttpResponseRedirect(reverse('index'))
                else:
                    messages.add_message(request, messages.ERROR, "激活失败，用户名或验证码错误")
                    return HttpResponseRedirect(reverse('index'))
            else:
                messages.add_message(request, messages.ERROR, "激活失败，用户名或验证码错误")
                return HttpResponseRedirect(reverse('index'))
        except ObjectDoesNotExist as e:
            messages.add_message(request, messages.ERROR, "激活失败，用户名或验证码错误")
            return HttpResponseRedirect(reverse('index'))

class LoginView2(View):
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cached_user)
            return JsonResponse({'status' : 200, 'errors' : {}, 'result' : {}})
        else:
            return JsonResponse({'status' : 400, 'errors' : json.loads(form.errors.as_json()), 'result' : {}})


class LoginView(FormView):      #登录
    form_class = LoginForm      #forms

    def form_valid(self, form):
        login(self.request, form.cached_user)
        return JsonResponse({'status' : 200, 'errors' : {}, 'result' : {}})

    def form_invalid(self, form):
        return JsonResponse({'status' : 400, 'errors' : json.loads(form.errors.as_json()), 'result' : {}})


class LogoutView(View):     #退出
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class ModifyPasswordView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponse('success')
        else:
            return HttpResponse('fail')



class ResetPasswordView(FormView):
    template_name = 'account/reset_password.html'
    form_class = ResetPasswordForm

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = form.cached_user
                validkey = user.userext.gen_validkey()
                user.userext.validkey = validkey
                user.userext.save()
                content = '欢迎使用[wp的商城], 请点击此处进行重置用户: http://192.168.1.116:8888/account/reset_password_confirm/?username={username}&validkey={validkey}'.format(username=user.username, validkey=validkey)
                send_mail('[KK的商城]用户重置密码', content, settings.EMAIL_HOST_USER, [user.email])
                messages.add_message(self.request, messages.INFO, '重置密码邮件已发送, 请查收邮件进行密码重置')
        except BaseException as e:
            print(e)
            messages.add_message(self.request, messages.ERROR, '重置密码邮件发送失败，请重试')

        return HttpResponseRedirect(reverse('index'))

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form' : form})


class ResetPasswordConfirmView(FormView):
    template_name = 'account/reset_password_confirm.html'
    form_class = ResetPasswordConfirmForm

    def get_initial(self):
        return self.request.GET

    def form_valid(self, form):
        user = form.cached_user
        password = form.cleaned_data.get('password', '')
        user.set_password(password)
        user.save()
        user.userext.validkey = ''
        user.userext.save()
        messages.add_message(self.request, messages.INFO, '重置密码成功，请重新登陆')
        return HttpResponseRedirect(reverse('index'))

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form' : form})


class ChangePasswordView(LoginRequiredMixin,FormView):      #修改密码,LoginRequiredMixin检查是否在登录状态以及权限
    form_class = ChangePasswordForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data.get('password', '')
        user.set_password(password)
        user.save()
        return JsonResponse({'status' : 200, 'errors' : {}, 'result' : None})

    def form_invalid(self, form):
        return JsonResponse({'status' : 400, 'errors' : json.loads(form.errors.as_json()), 'result' : None})


@login_required
@timing
def test():
    time.sleep(4)
    return HttpResponse('ok')


class UserExtBaseView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'account/user_ext.html'
    form_class = UserExtBaseForm
    form_class_avatar = UserExtAvatarForm

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
                                    'form' : self.form_class(instance=request.user.userext),
                                    'form_avatar' : self.form_class_avatar(instance=request.user.userext),
                                    'nav' : 'base'
                                    })  #给render_to_response提供content

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=request.user.userext)
        if form.is_valid():
            model = form.save(commit=False)
            model.save()

        return self.render_to_response({
                                        'form' : form,
                                        'form_avatar' : self.form_class_avatar(instance=request.user.userext),
                                        'nav' : 'base'
                                        })


class UserExtAvatarView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'account/user_ext.html'
    form_class = UserExtBaseForm
    form_class_avatar = UserExtAvatarForm

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
                                    'form' : self.form_class(instance=request.user.userext),#instance 初始化填充数据，在form内用initial。
                                    'form_avatar' : self.form_class_avatar(instance=request.user.userext),
                                    'nav' : 'avatar'
                                    })

    def post(self, request, *args, **kwargs):
        form = self.form_class_avatar(data=request.POST, files=request.FILES, instance=request.user.userext)
        if form.is_valid():
            avatar = request.FILES.get('avatar', None)
            if avatar:
                name = '{pk}_{ctime}.{suffix}'.format(pk=request.user.pk, ctime=int(time.time() * 1000), suffix=avatar.name.split('.')[-1])
                path = os.path.join(settings.MEDIA_ROOT, 'avatar', name)
                with open(path, 'wb') as fhandler:
                    for chunk in avatar.chunks():
                        fhandler.write(chunk)

                model = form.save(commit=False)
                model.avatar = name
                model.save()

        return self.render_to_response({
                                        'form': self.form_class(instance=request.user.userext),
                                        'form_avatar': form,
                                        'nav': 'avatar'
                                        })


class UserAddressListView(LoginRequiredMixin, ListView):
    model=UserAddress
    template_name ='account/user_address.html'

    def get_queryset(self):
        return self.model.objects.filter(status=1,user=self.request.user)



class UserAddressCreateView(LoginRequiredMixin, CreateView):    #添加收货地址
    template_name = 'account/user_address_create.html'
    model = UserAddress
    form_class = UserAddressForm
    def form_valid(self,form):
        obj=form.save(commit=False)
        obj.user=self.request.user
        obj.status=1
        obj.save()
        return HttpResponseRedirect(reverse('account:user_address'))


class test_args_kwargs(View):
    def get(self,request,*args,**kwargs):
        print(args)
        print(kwargs)
        return HttpResponse('ok')

class UserAddressDeleteView(LoginRequiredMixin,ObjectPermMixin, DeleteView):
    model = UserAddress
    #def get(self,request,*args,**kwargs):
    #    obj = self.get_object()
    #    if obj.user == request.user:
    #        return super().get(self,request,*args,**kwargs)
     #   else:
     #       raise Http404('对象不存在')
    def delete(self,request,*args,**kwargs):
        obj=self.get_object()
     #   if obj.user==request.user:
        obj.status=0
        obj.save()
        return HttpResponseRedirect(reverse('account:user_address'))


class UserAddressUpdateView(LoginRequiredMixin,ObjectPermMixin,UpdateView):
    template_name = 'account/user_address_create.html'
    model = UserAddress
    form_class = UserAddressForm
    success_url=reverse_lazy('account:user_address')
