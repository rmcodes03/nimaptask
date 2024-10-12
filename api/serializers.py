from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, Project

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ProjectSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'users', 'created_at']

class ClientSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Client
        fields = ['id', 'client_name', 'created_by', 'created_at', 'updated_at']

class CreateProjectSerializer(serializers.ModelSerializer):
    users = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    client = serializers.CharField(source='client.client_name', read_only=True)
    created_by = serializers.CharField(source='client.created_by.username', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'client', 'users', 'created_at', 'created_by']

    def create(self, validated_data):
        users_data = validated_data.pop('users')
        project = Project.objects.create(**validated_data)
        
        for user_data in users_data:
            user = User.objects.get(id=user_data['id'])
            project.users.add(user)
        
        return project

    def to_representation(self, instance):
        """Customize the response to show user details."""
        response = super().to_representation(instance)
        response['users'] = [
            {'id': user.id, 'name': user.username}
            for user in instance.users.all()
        ]
        return response
