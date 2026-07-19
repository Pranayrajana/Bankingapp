from django.contrib import admin
from .models import Account, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "user", "account_type", "balance", "created_at")
    search_fields = ("account_number", "user__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "transaction_type", "amount", "balance_after", "timestamp")
    list_filter = ("transaction_type",)
    search_fields = ("account__account_number",)
