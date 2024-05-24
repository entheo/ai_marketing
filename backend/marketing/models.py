from django.db import models
from django.db.models import JSONField
from account.models import Users 
from django.utils import timezone

# Create your models here.

class IndustryTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class EmotionTag(models.Model):
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag


# 品牌模型
class Brand(models.Model):
    chinese_name = models.CharField(max_length=255, unique=True)
    english_name = models.CharField(max_length=255, null=True,blank=True)
    values = models.TextField(null=True, blank=True)
    audience = models.TextField(null=True, blank=True)
    emotion_tags = models.ManyToManyField(EmotionTag, related_name='brands', blank=True)
    competitors = models.TextField(null=True,blank=True)
    regions = models.CharField(max_length=255,default='中国大陆')
    industry_tags = models.ManyToManyField(IndustryTag, related_name='brands', blank=True)
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='brands',default='1')
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)      

    def add_emotion_tag(self, tag_str):
        tag, created = EmotionTag.objects.get_or_create(tag=tag_str)
        self.emotion_tags.add(tag)

    def remove_emotion_tag(self, tag_str):
        try:
            tag = EmotionTag.objects.get(tag=tag_str)
            self.emotion_tags.remove(tag)
        except EmotionTag.DoesNotExist:
            pass

    def update_emotion_tag(self, old_tag_str, new_tag_str):
        try:
            tag = self.emotion_tags.get(tag=old_tag_str)
            tag.tag = new_tag_str
            tag.save()
        except EmotionTag.DoesNotExist:
            pass
    
    def get_emotion_tags_list(self):
        return list(self.emotion_tags.values_list('tag', flat=True))
    
    def __str__(self):
        return self.chinese_name

# 目标用户模型
class Persona(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='personas',default='1')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ...其他描述目标用户的字段

# 产品模型
class Product(models.Model):
    chinese_name = models.CharField(max_length=255)
    english_name = models.CharField(max_length=255,null=True,blank=True)
    usp = JSONField(blank=True, null=True) 
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    personas = models.ManyToManyField(Persona, related_name='products')
    description = models.TextField()
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='products',default= '1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #price = models.DecimalField(max_digits=10, decimal_places=2)
    # ...其他产品相关的字段
