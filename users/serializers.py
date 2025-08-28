from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with role management
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone', 'role', 'is_active', 'created_at', 'updated_at',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing users
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information (without password)
    """
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'is_active'
        ]
