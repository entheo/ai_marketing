from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission


# Create your models here.
USER_TYPES = (
    ('个人用户', '个人用户'),
    ('企业用户', '企业用户'),
)

class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('必须有一个用户名')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须有 is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须有 is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=128, unique=True)
    wechat_openID = models.CharField(max_length=128, unique=True, null=True, blank=True)
    wechat_nickname = models.CharField(max_length=128, null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    user_type = models.CharField(max_length=32, choices=USER_TYPES)
    trial_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = MyUserManager()

    # 修改默认的 related_name 以避免与内置 User 模型冲突
    groups = models.ManyToManyField(
        Group,
        verbose_name='用户组',
        blank=True,
        help_text='指定该用户所属的组',
        related_name="custom_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='用户权限',
        blank=True,
        help_text='指定用户的特定权限',
        related_name="custom_user_permissions",
        related_query_name="user",
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

class InvitationCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code
