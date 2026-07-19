from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Account


class RegisterForm(UserCreationForm):
    """Extends Django's built-in user creation form, and lets the user
    pick a starting account type. We don't collect real personal/financial
    data here since this is a learning project, not a production bank."""
    account_type = forms.ChoiceField(choices=Account.ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "account_type"]


class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    note = forms.CharField(max_length=255, required=False)


class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    note = forms.CharField(max_length=255, required=False)


class TransferForm(forms.Form):
    to_account_number = forms.CharField(max_length=12, label="Recipient account number")
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    note = forms.CharField(max_length=255, required=False)
