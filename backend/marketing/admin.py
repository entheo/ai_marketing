from django.contrib import admin
from .models import Brand,Campaign
# Register your models here.

class BrandAdmin(admin.ModelAdmin):
    list_display = ['chinese_name', 'created_at']  
    search_fields = ['chinese_name']  # 可以添加搜索字段

class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title','created_at']
    search_fields = ['title']


# 注册模型及其Admin类
admin.site.register(Brand, BrandAdmin)
admin.site.register(Campaign,CampaignAdmin)
