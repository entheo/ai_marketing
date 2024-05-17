from django.db import models

# Create your models here.

from django.db import models

# 用户类型的选择
USER_TYPES = (
    ('个人用户', '个人用户'),
    ('企业用户', '企业用户'),
)

class Users(models.Model):
    userID = models.AutoField(primary_key=True)
    wechat_openID = models.CharField(max_length=128, unique=True)
    wechat_nickname = models.CharField(max_length=128)
    avatar_url = models.URLField()
    user_type = models.CharField(max_length=32, choices=USER_TYPES)
    trial_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
