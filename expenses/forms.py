from django import forms
from .models import Expense, CATEGORY_CHOICES, Budget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
# forms.py
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'note']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.RadioSelect(),   # keep radios
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #  REMOVE "---------"
        self.fields['category'].choices = [
            choice for choice in self.fields['category'].choices
            if choice[0] != ""
        ]

        self.fields['category'].required = True

# Register form
# class RegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    profession = forms.CharField(required=False)
    address = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = User
        fields = [
            'username', 'email',
            'first_name', 'middle_name', 'last_name',
            'dob', 'profession', 'address',
            'password1', 'password2'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists!")

        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists!")

        return username

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'month', 'year', 'amount']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2100}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
