# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Users
from .models import InvitationCode


class UserRegistrationSerializer(serializers.ModelSerializer):
    invitation_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = Users
        fields = ('username', 'password', 'invitation_code')
    
    def validate_invitation_code(self, value):
        """
        验证提供的邀请码是否有效
        """
        try:
            invite = InvitationCode.objects.get(code=value, is_used=False)
        except InvitationCode.DoesNotExist:
            raise serializers.ValidationError("无效的邀请码。")
        return value
    
    def create(self, validated_data):
        """
        创建新用户实例，使用有效的邀请码
        """
        invitation_code = validated_data.pop('invitation_code')
        user = Users.objects.create_user(**validated_data)
        invite = InvitationCode.objects.get(code=invitation_code)
        invite.is_used = True
        invite.save()
        return user
