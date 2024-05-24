from rest_framework import serializers
from .models import Brand
from account.models import Users

class BrandSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ['creator'] 
