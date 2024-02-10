from datetime import datetime
from django.db import models

# Create your models here.
import uuid

from django.db.models.signals import pre_save, post_save
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


from rest_framework import status
from rest_framework.response import Response

from files.models import TimeStamps
from properties.models import Property

from utils.utils import CustomUUIDField, customResponse


UNIT_TYPE_CHOICES = [
    ('Apartment', _('Apartment')),
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

UNIT_STATUS = [
    ('Vacant', _('Vacant')),
    ('Occupied', _('Occupied'))
]

class Units(TimeStamps):
    id               = CustomUUIDField()
    unit_number      = models.CharField(max_length=255)
    size             = models.DecimalField(max_digits=8, decimal_places=2)
    bedrooms         = models.IntegerField()
    bathrooms        = models.IntegerField()
    amenities        = models.JSONField(blank=True, null=True)
    monthly_rent     = models.IntegerField(null=True)
    unit_type        = models.CharField(max_length=50, choices=UNIT_TYPE_CHOICES, blank=True, null=True)
    property         = models.ForeignKey(Property, related_name="units", on_delete=models.CASCADE, blank=True, null=True)
    account          = models.CharField(max_length=100, blank=True)
    status           = models.CharField(max_length=50, choices=UNIT_STATUS, default="Vacant")

    def __str__(self):
        return self.unit_number
    
    class Meta:
        db_table="units"


class Assignment(models.Model):
    id               = CustomUUIDField()
    tenant           = models.CharField(max_length=50)
    unit             = models.ForeignKey(Units, on_delete=models.CASCADE)
    property         = models.ForeignKey(Property, on_delete=models.CASCADE, null=True)
    assigned_date    = models.DateTimeField(auto_now_add=True)
    vacated_date     = models.DateField(blank=True, null=True)


    def __str__(self):
        return self.unit.unit_number
    
    @classmethod
    def vacate_unit(cls, unit):
        assignment = cls.objects.get(unit=unit, vacated_date__isnull=True)
        assignment.vacated_date = timezone.now().date()
        assignment.save()
        unit.status = 'Vacant'  # Update unit status to 'Vacant'
        unit.save()
        
    @classmethod
    def swap_units(cls, unit1, unit2):
        assignment1 = cls.objects.filter(unit=unit1, vacated_date__isnull=True).first()
        assignment2 = cls.objects.filter(unit=unit2, vacated_date__isnull=True).first()
        
        if assignment1 and assignment2:
            assignment1.unit = unit2
            assignment1.save()
            assignment2.unit = unit1
            assignment2.save()
    
    class Meta:
        db_table="unit_assignment"

