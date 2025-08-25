from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('accountant', 'Accountant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')
    # 2FA secret
    two_factor_secret = models.CharField(max_length=255, blank=True, null=True)

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Equity', 'Equity'),
        ('Revenue', 'Revenue'),
        ('Expense', 'Expense'),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
