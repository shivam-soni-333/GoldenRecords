from django.db import models
from dashboard.models import Invoice,Silver_Invoice

# Create your models here.
class Income(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=200)
    amount = models.FloatField()

    def __str__(self):
        return (self.description)

class Expense(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=200)
    amount = models.FloatField()

    def __str__(self):
        return (self.description)
    
class opening_balance(models.Model):
    date = models.DateField()
    time = models.TimeField(auto_now=True)
    balance = models.FloatField()

    def __str__(self):
        return ("Last Updated:-" +str(self.date))
    
