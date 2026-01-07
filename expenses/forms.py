from django import forms
from .models import Expense, CATEGORY_CHOICES, Budget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

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
