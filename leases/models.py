from django.db import models
from django.utils.translation import gettext_lazy as _


from files.models import Files, TimeStamps
from properties.models import Property
from units.models import Units

from utils.utils import CustomUUIDField

TERMS = [
    ('Fixed Term', _('Fixed Term')),
    ('Month-To-Month', _('Month-To-Month')),
]

FREQUENCY = [
    ('Daily', _('Daily')),
    ('Weekly', _('Weekly')),
    ('Every 2 Weeks', _('Every 2 Weeks')),
    ('Monthly', _('Monthly')),
    ('Quarterly', _('Quarterly')),
    ('Semi Annual', _('Semi Annual')),
    ('Annually', _('Annually')),
]

# Create your models here.
class Lease(TimeStamps):
    id               = CustomUUIDField()
    property         = models.ForeignKey(Property, on_delete=models.CASCADE)
    unit             = models.ForeignKey(Units, on_delete=models.CASCADE)
    tenant           = models.JSONField()
    term             = models.CharField(max_length=50, choices=TERMS, blank=True, null=True)
    rent             = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    rent_frequency   = models.CharField(max_length=50, choices=FREQUENCY)
    due_day          = models.IntegerField(null=True)
    start_date       = models.DateField(blank=True, null=True)
    end_date         = models.DateField(blank=True, null=True)
    file             = models.ForeignKey(Files, on_delete=models.CASCADE)
    account          = models.CharField(max_length=50)

    def __str__(self):
        return self.property

    class Meta:
        db_table = 'leases'
        verbose_name_plural = 'Leases'

    



class Bills(TimeStamps):
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='bills')
    item = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField()
    rate = models.IntegerField()
    amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.item

    class Meta:
        db_table = 'bills'
        verbose_name_plural = 'Bills'
