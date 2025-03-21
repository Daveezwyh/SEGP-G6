from django.db import models
from django.contrib.auth.models import User
import os
import uuid
from enum import Enum
from autoclean.scanners.result import ScanResult
from autoclean.scanners.result import ScanResultAction

def get_random_filename(instance, filename):
    random_filename = f"{uuid.uuid4()}.{filename.split('.')[-1]}"
    return os.path.join('imports', random_filename)

class Import(models.Model):
    class Status(models.IntegerChoices):
        NEW = 1, "New"
        PROCESSING = 2, "Processing"
        COMPLETED = 3, "Completed"
        FAILED = 4, "Failed"
    
    description = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_random_filename, null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)

    class Meta:
        ordering = ["id"]
    
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

class ImportDataOriginal(models.Model):
    import_model = models.ForeignKey(Import, related_name="import_data_ori", on_delete=models.CASCADE)
    data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class ImportScanResult(models.Model):
    id = models.AutoField(primary_key=True)
    row = models.IntegerField()
    col = models.IntegerField()
    message = models.CharField(max_length=255)
    action_type = models.IntegerField(default=0)
    priority = models.IntegerField(default=1000, db_index=True)
    import_model = models.ForeignKey(Import, related_name="scan_results", on_delete=models.CASCADE)

    def transform(self):
        scan_result = ScanResult(
            row=self.row,
            col=self.col,
            message=self.message,
            action_type=self.action_type,
            actions=[action.transform() for action in self.actions.all()]
        )
        return scan_result

class ImportScanResultAction(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    cleaner = models.CharField(max_length=255, null=True, blank=True)
    cleaner_id = models.IntegerField(null=True, blank=True)
    activate = models.BooleanField(default=False)
    data = models.JSONField(null=True, blank=True)
    import_scan_result = models.ForeignKey(ImportScanResult, related_name="actions", on_delete=models.CASCADE)

    def transform(self):
        return ScanResultAction(
            title=self.title,
            description=self.description,
            cleaner=self.cleaner,
            cleaner_id=self.cleaner_id,
            activate=self.activate,
            data=self.data
        )

class TaskProgress(models.Model):
    class Status(str, Enum):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        ERROR = "error"

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(
        max_length=50,
        choices=[(status.value, status.value) for status in Status],
        default=Status.PENDING.value,
    )
    message = models.CharField(max_length=255)
    error = models.TextField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    data = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @staticmethod
    def makeUUID():
        return uuid.uuid4()

class Cleaner(models.Model):
    id = models.AutoField(primary_key=True)
    fn_name = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=255, null=False, blank=False)
    status = models.SmallIntegerField(default=0)
    definition = models.TextField(null=False, blank=False)
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name