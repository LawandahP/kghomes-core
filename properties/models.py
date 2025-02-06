from django.db import models
from django.template.defaultfilters import slugify

from django.db.models.signals import pre_save
from django.dispatch import receiver
from files.models import Files, TimeStamps

from utils.utils import CustomUUIDField
from utils.utils import create_uuid

class PropertyAmenities(TimeStamps):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.CharField(max_length=100)
    account = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table="property_amenities"
        verbose_name_plural="Property Amenities"
        constraints = [
            models.UniqueConstraint(fields=['name', 'created_by', 'account'], name='unique_amenity_per_user_and_account')
        ]
        
# Category model (e.g., Residential, Commercial)
class Category(TimeStamps):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # Optional for extra context

    def __str__(self):
        return self.name
    
    class Meta:
        db_table="categories"
        verbose_name_plural="Categories"

# PropertyType model (e.g., Apartment, Condo, Office Space)
class PropertyType(TimeStamps):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # Optional for additional context
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='property_types')
    created_by = models.CharField(max_length=100)
    account = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    class Meta:
        db_table="property_types"
        verbose_name_plural="Property Types"
        constraints = [
            models.UniqueConstraint(fields=['name', 'created_by', 'account'], name='unique_property_type_per_user_and_account')
        ]


class Property(TimeStamps):
    id = CustomUUIDField()
    name = models.CharField(max_length=255)

    address = models.JSONField(null=True, blank=True)
    latlng = models.JSONField(null=True, blank=True)
    bounds = models.JSONField(null=True, blank=True)

    description = models.TextField(max_length=255, null=True, blank=True)
    property_type = models.CharField(max_length=100, blank=True, null=True)
    amenities = models.JSONField(null=True, blank=True)
    
    slug = models.SlugField(blank=True, null=True)
    images = models.ManyToManyField(Files, blank=True, related_name="property_images")
    owner = models.CharField(max_length=255)
    account = models.CharField(max_length=100, blank=True)

    has_units = models.BooleanField(default=True)
    unit_count = models.PositiveIntegerField(blank=True, null=True)
    vacant_units_count = models.PositiveIntegerField(blank=True, null=True)
    rented_units_count = models.PositiveIntegerField(blank=True, null=True)


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
   
 