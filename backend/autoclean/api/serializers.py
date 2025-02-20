from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Import, ImportData, ImportScanResult, TaskProgress

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('is_staff', 'is_superuser')

class TaskProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskProgress
        fields = ['uuid', 'status', 'message', 'error', 'percentage', 'data']

class UploadImportSerializer(serializers.ModelSerializer):
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

class ImportSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SerializerMethodField()
    file = serializers.CharField(write_only=True)

    class Meta:
        model = Import
        fields = ['id', 'description', 'data', 'uploaded_at', 'uploaded_by', 'file']
        read_only_fields = ['uploaded_at', 'uploaded_by', 'data']
    
    def get_uploaded_by(self, obj) -> str:
        return obj.uploaded_by.username if obj.uploaded_by else None

class ImportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportData
        fields = ['id', 'data', 'created_at']

class ImportScanResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportScanResult
        fields = ['id', 'row', 'col', 'message', 'action_type']

class ImportScanResultUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    import_model_id = serializers.IntegerField(required=True)
    activate = serializers.BooleanField(required=True)

    class Meta:
        model = ImportScanResult
        fields = ["id", "import_model_id", "activate"]