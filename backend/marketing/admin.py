from django.contrib import admin
from .models import Brand
# Register your models here.

class BrandAdmin(admin.ModelAdmin):
    list_display = ['chinese_name', 'created_at']  # 这里列出你想要显示的字段名称
    search_fields = ['chinese_name']  # 可以添加搜索字段

# 注册模型及其Admin类
admin.site.register(Brand, BrandAdmin)
