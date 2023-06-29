from rest_framework import serializers
from .models import CustomUser, Post, Like


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    

class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'email', 'is_admin', 'is_active')


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('image', 'title', 'description', 'visibility', 'user_id')


class ReadPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'image', 'title', 'description', 'created_at', 'visibility', 'user_id', 'like_count')


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"