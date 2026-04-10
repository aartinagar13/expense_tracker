# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('Travel', 'Travel'),
    ('Business', 'Business'),
    ('Education', 'Education'),
    ('Food', 'Food'),
    ('Clothing', 'Clothing'),
    ('Rent', 'Rent'),
    ('Bills', 'Bills'),
    ('Enjoyment', 'Enjoyment'),
    ('Other', 'Other'),
]
MONTH_CHOICES = [
    ('Jan', 'January'), ('Feb', 'February'), ('Mar', 'March'),
    ('Apr', 'April'), ('May', 'May'), ('Jun', 'June'),
    ('Jul', 'July'), ('Aug', 'August'), ('Sep', 'September'),
    ('Oct', 'October'), ('Nov', 'November'), ('Dec', 'December'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    profession = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.FloatField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Budget(models.Model):
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=3, choices=MONTH_CHOICES)
    year = models.IntegerField(default=timezone.now().year)

    def __str__(self):
        return f"{self.category} - {self.month}/{self.year}"