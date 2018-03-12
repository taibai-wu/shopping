#encoding:utf-8
from django.http import HttpResponse
from functools import wraps
import time

def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        print('before')
        rt=func(*args,**kwargs)
        print('after')
        return rt
    return wrapper

def timing(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        s=time.time()
        rt=func(*args,**kwargs)
        print(func.__name__,'total time:',time.time() - s)
        return rt
    return wrapper



@login_required
def test1():
    time.sleep(2)



@login_required
@timing
def test2():
    time.sleep(4)

test1()
test2()
