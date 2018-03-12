#encoding:utf-8

from django.contrib import admin

from .models import Category,Goods,GoodsExt, Order, GoodsBuied
from .forms import GoodsAdminForm, OrderAdminForm
# Register your models here.
admin.site.site_header='吴鹏的商城header'
admin.site.site_title='吴鹏的商城title'



class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','create_time']   #此处用来在 后端修改商品分类 时显示
    fields = ['name']       #增加分类时，只增加name
    search_fields = ['name']    #按name进行查找
    actions = None

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(status=1)

    def delete_model(self, request, obj):
        obj.status=0
        obj.save()

class GoodsExtInline(admin.TabularInline):  #admin.StackedInline 堆栈型。
    model = GoodsExt
    fields = ['key','value']
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(status=1)




class GoodsAdmin(CategoryAdmin):
    list_display = ['category','name', 'price','store']
    fields = ['category','name','price','img','create_time','store','desc']
    #exclude=['status'] #此处为继承关系上边定义的fields，下边要改也得用fields
    form = GoodsAdminForm
    search_fields = ['name','desc','category__name']    #,'category__name' 通过关联性进行查找
    inlines = [GoodsExtInline]      #引入inlines，将GoodsExt的内容家到Goods上

    def save_formset(self, request, form, formset, change):
        instances=formset.save(commit=False)    #commit=False   不同步数据库
        for obj in formset.deleted_objects:
            obj.status = 0
            obj.save()

        for obj in instances:   #手动进行数据库同步
            obj.save()

        formset.save_m2m()  #多对多借助中间表存储


class GoodsBuiedInline(admin.TabularInline):
    model = GoodsBuied
    fields = ['goods', 'num', 'price']
    readonly_fields = ['price', 'goods', 'num']
    extra = 0
    can_delete = False

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'price', 'create_time', 'status_text', 'is_normal']
    actions = None
    readonly_fields = ['user', 'price', 'user_address', 'invoice_type', 'invoice_title', 'pay_type', 'create_time', 'status_text']
    form = OrderAdminForm
    inlines = [
        GoodsBuiedInline
    ]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(Order, OrderAdmin)

