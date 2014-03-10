from django.contrib.auth.models import User
from rest_framework import serializers
from student.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username")
        read_only_fields = ("id", "email", "username")
