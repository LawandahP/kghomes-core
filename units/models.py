from django.db import models

# Create your models here.
import uuid

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


from django.db import models
from files.models import TimeStamps
from properties.models import Property

from utils.utils import CustomUUIDField
# from properties.models import Property

UNIT_TYPE_CHOICES = [
    ('1+ Bedrooms', _('1+ Bedrooms')),
    ('Studio', _('Studio')),
    ('Single Room', _('Single Room')),
    ('Shop', _('Shop')),
    ('Office', _('Office')),
    ('Warehouse', _('Warehouse')),
    ('Garage', _('Garage')),
    ('Restaurant', _('Restaurant')),
    ('Clinic', _('Clinic')),
    # Add more choices as needed
]

class Units(TimeStamps):
    id               = CustomUUIDField()
    unit_number      = models.CharField(max_length=255)
    size             = models.DecimalField(max_digits=8, decimal_places=2)
    bedrooms         = models.IntegerField()
    bathrooms        = models.IntegerField()
    amenities        = models.JSONField(blank=True, null=True)
    monthly_rent     = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    unit_type        = models.CharField(max_length=50, choices=UNIT_TYPE_CHOICES, blank=True, null=True)
    property         = models.ForeignKey(Property, related_name="units", on_delete=models.CASCADE, blank=True, null=True)
    account          = models.CharField(max_length=100, blank=True)
    # images           = models.ManyToManyField(Files, blank=True)

    def __str__(self):
        return self.unit_number

    class Meta:
        db_table="units"


class Assignment(TimeStamps):
    id               = CustomUUIDField()
    tenant           = models.JSONField()
    unit             = models.ForeignKey(Units, on_delete=models.CASCADE)
    assigned_date    = models.DateTimeField(auto_now_add=True)
    monthly_rent     = models.DecimalField(max_digits=10, decimal_places=2)
    notes            = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.unit.unit_number

    class Meta:
        db_table="unit_assignment"

