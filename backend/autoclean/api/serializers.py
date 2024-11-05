from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Import

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('is_staff', 'is_superuser')

class ImportSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Import
        fields = ['id', 'description', 'data', 'uploaded_at', 'uploaded_by', 'file']
        read_only_fields = ['uploaded_at', 'uploaded_by', 'data']
    
    def validate(self, attrs):
        if 'file' not in attrs or attrs['file'] is None:
            raise serializers.ValidationError({"file": "Import file is required."})
        
        max_file_size_MB = 10
        max_file_size = max_file_size_MB * 1024 * 1024
        file = attrs['file']
        if file.size > max_file_size:
            raise serializers.ValidationError({"file": f"File size must not exceed {max_file_size_MB} MB."})
        
        if file.content_type not in Import.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError({"file": "Only CSV or Excel files are allowed."})
        
        return attrs
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        filename = instance.data.get('filename') if instance.data else None
        
        return {
            "id": representation["id"],
            "description": representation["description"],
            "filename": filename
        }