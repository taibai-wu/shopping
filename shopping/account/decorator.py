from django.http import HttpResponse

def login_required(func):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated():
            rt=func(request,*args,**kwargs)
            return rt
        else:
            return HttpResponse('未登录')
    return wrapper

def timing(func):
    #@wraps(func)
    def wrapper(request,*args,**kwargs):
        s=time.time()
        rt=func(request,*args,**kwargs)
        print(func.__name__,'total time:',time.time() - s)
        return rt
    return wrapper


