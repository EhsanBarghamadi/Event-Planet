import re
from rest_framework import serializers
from .models import CustomUser


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['phone', 'first_name', 'last_name', 'role', 'password']

    def validate_phone(self, value):
        pattern = r"^(\+98|0)?9\d{9}$"
        match = re.match(pattern, value)
        if not match:
            raise serializers.ValidationError('شماره وارد شده معتبر نیست!')
        return value
    
    def create(self, validated_data):
        phone = validated_data.pop('phone')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(phone, password, **validated_data)
        return user