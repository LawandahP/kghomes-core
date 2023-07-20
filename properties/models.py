from django.db import models
from django.template.defaultfilters import slugify

from django.db.models.signals import pre_save
from django.dispatch import receiver
from utils.utils import CustomUUIDField

from utils.utils import create_uuid


class Kind(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'property_kind'
        verbose_name_plural="Property Kind"
    

class Type(models.Model):
    kind = models.ForeignKey(Kind, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'property_type'
        verbose_name_plural="Property Types"
    

class Amenities(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        db_table = 'amenities'
        verbose_name_plural = 'Amenities'


class Property(models.Model):
    id = CustomUUIDField()
    name = models.CharField(max_length=255, null=True)
    property_kind = models.ForeignKey(Kind, blank=True, on_delete=models.CASCADE, null=True)
    property_type = models.ForeignKey(Type, blank=True, on_delete=models.CASCADE, null=True)
    address = models.TextField(max_length=255, blank=True, null=True)
    amenities = models.ManyToManyField(Amenities, related_name="amenities", blank=True)
    slug = models.SlugField(blank=True, null=True)
    # images = models.ManyToManyField(Files, blank=True, related_name="property_images")
    owner = models.CharField(max_length=255, blank=True, null=True)
    account = models.CharField(max_length=255)

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
   
