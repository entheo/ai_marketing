from django.contrib import admin
from .models import Users
# Register your models here.
from .models import InvitationCode

# 可选：自定义Admin界面
class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'created_at']  # 这里列出你想要显示的字段名称
    search_fields = ['code']  # 可以添加搜索字段

# 注册模型及其Admin类
admin.site.register(InvitationCode, InvitationCodeAdmin)
admin.site.register(Users)
