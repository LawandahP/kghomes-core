# from django.db import models

# # Create your models here.
# import uuid

# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver

# from django.db import models
# from accounts.models import CustomUUIDField
# # from properties.models import Property
# from users.models import User

# class Unit(models.Model):
#     id = CustomUUIDField()
#     unit_no          = models.CharField(max_length=255)
#     square_feet      = models.CharField(max_length=255, blank=True, null=True)
#     bedrooms         = models.IntegerField()
#     bathrooms        = models.IntegerField()
#     # property         = models.ForeignKey(Property, related_name="units", on_delete=models.CASCADE, blank=True, null=True)
#     # previous_tenants = models.ManyToManyField(Tenant, related_name="previous_tenants", blank=True)
#     # images           = models.ManyToManyField(Files, blank=True)
#     tenant           = models.OneToOneField(User, related_name="occupant", unique=True, on_delete=models.SET_NULL, blank=True, null=True)
#     slug             = models.SlugField(blank=True, null=False)

#     def __str__(self):
#         return self.unit_no

#     class Meta:
#         db_table="units"
