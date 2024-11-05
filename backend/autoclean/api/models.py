from django.db import models
from django.contrib.auth.models import User
import os
import uuid

def get_random_filename(instance, filename):
    random_filename = f"{uuid.uuid4()}.{filename.split('.')[-1]}"
    return os.path.join('imports', random_filename)

class Import(models.Model):
    description = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_random_filename, null=True, blank=True)

    ALLOWED_CONTENT_TYPES = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ]

    def __str__(self):
        return self.description

class ImportData(models.Model):
    import_model = models.ForeignKey(Import, related_name="import_data", on_delete=models.CASCADE)
    data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
