from rest_framework import serializers
from .models import Brand, Campaign
from account.models import Users

class BrandSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ['creator']

class CampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['creator']
