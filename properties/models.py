from django.db import models
from django.template.defaultfilters import slugify

from django.db.models.signals import pre_save
from django.dispatch import receiver


from utils.utils import CustomUUIDField
from utils.utils import create_uuid



class Property(models.Model):
    id = CustomUUIDField()
    name = models.CharField(max_length=255, null=False, blank=False)

    address = models.JSONField(null=True, blank=True)
    latlng = models.JSONField(null=True, blank=True)
    bounds = models.JSONField(null=True, blank=True)

    description = models.TextField(max_length=255, null=True, blank=True)
    property_type = models.CharField(max_length=100, blank=True, null=True)
    amenities = models.JSONField(null=True, blank=True)
    
    slug = models.SlugField(blank=True, null=True)
    # images = models.ManyToManyField(Files, blank=True, related_name="property_images")
    owner = models.JSONField(blank=True, null=True)
    account = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table="properties"
        verbose_name_plural="Properties"


@receiver(pre_save, sender=Property)
def pre_save_account_signal(sender, instance, *args, **kwargs):
    unique_code = create_uuid()
    if not instance.slug:
        instance.slug = slugify(instance.name + "-" + unique_code)
   
 