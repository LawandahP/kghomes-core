from django.utils import timezone
from django.db import models

from utils.utils import CustomUUIDField


# Create your models here.
class TimeStamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

class Files(TimeStamps):
    id = CustomUUIDField()
    file_url = models.FileField(blank=True, null=True, upload_to="files")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.file_url)
    
    class Meta:
        db_table = 'files'
        verbose_name_plural = 'Files'