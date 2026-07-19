from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid


class Account(models.Model):
    """
    One bank Account per User.
    We keep 'balance' as the single source of truth for how much money
    a user has. Every deposit/withdraw/transfer updates this field
    AND creates a Transaction record, so we always have a paper trail.
    """
    ACCOUNT_TYPE_CHOICES = [
        ("SAVINGS", "Savings"),
        ("CURRENT", "Current"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default="SAVINGS")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            # Simple, readable way to generate a unique-looking account number
            self.account_number = uuid.uuid4().int.__str__()[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"


class Transaction(models.Model):
    """
    Immutable log of every money movement.
    For a transfer, we create TWO rows (one DEBIT for sender, one CREDIT
    for receiver) linked by the same 'reference' so the history page can
    show a full audit trail for both accounts.
    """
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
        ("TRANSFER_OUT", "Transfer Sent"),
        ("TRANSFER_IN", "Transfer Received"),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=40, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.account.account_number}"
