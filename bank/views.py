import uuid

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.shortcuts import render, redirect

from .forms import RegisterForm, DepositForm, WithdrawForm, TransferForm
from .models import Account, Transaction


def register_view(request):
    """Sign up a new user AND create their Account in one step,
    so every user always has exactly one account (see Account.user
    OneToOneField in models.py)."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(
                user=user,
                account_type=form.cleaned_data["account_type"],
            )
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "bank/register.html", {"form": form})


@login_required
def dashboard_view(request):
    account = request.user.account
    recent_transactions = account.transactions.all()[:5]
    return render(request, "bank/dashboard.html", {
        "account": account,
        "recent_transactions": recent_transactions,
    })


@login_required
def deposit_view(request):
    account = request.user.account
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            # db_transaction.atomic() makes the balance update and the
            # transaction log write happen together - if one fails, both
            # roll back, so the ledger can never get out of sync.
            with db_transaction.atomic():
                account.balance += amount
                account.save()
                Transaction.objects.create(
                    account=account,
                    transaction_type="DEPOSIT",
                    amount=amount,
                    balance_after=account.balance,
                    note=form.cleaned_data.get("note"),
                )
            messages.success(request, f"Deposited {amount} successfully.")
            return redirect("dashboard")
    else:
        form = DepositForm()
    return render(request, "bank/deposit.html", {"form": form, "account": account})


@login_required
def withdraw_view(request):
    account = request.user.account
    if request.method == "POST":
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            if amount > account.balance:
                messages.error(request, "Insufficient balance.")
            else:
                with db_transaction.atomic():
                    account.balance -= amount
                    account.save()
                    Transaction.objects.create(
                        account=account,
                        transaction_type="WITHDRAW",
                        amount=amount,
                        balance_after=account.balance,
                        note=form.cleaned_data.get("note"),
                    )
                messages.success(request, f"Withdrew {amount} successfully.")
                return redirect("dashboard")
    else:
        form = WithdrawForm()
    return render(request, "bank/withdraw.html", {"form": form, "account": account})


@login_required
def transfer_view(request):
    account = request.user.account
    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            to_number = form.cleaned_data["to_account_number"]

            try:
                to_account = Account.objects.get(account_number=to_number)
            except Account.DoesNotExist:
                messages.error(request, "Recipient account not found.")
                return render(request, "bank/transfer.html", {"form": form, "account": account})

            if to_account.pk == account.pk:
                messages.error(request, "You cannot transfer to your own account.")
            elif amount > account.balance:
                messages.error(request, "Insufficient balance.")
            else:
                reference = str(uuid.uuid4())[:8]
                with db_transaction.atomic():
                    account.balance -= amount
                    account.save()
                    Transaction.objects.create(
                        account=account,
                        transaction_type="TRANSFER_OUT",
                        amount=amount,
                        balance_after=account.balance,
                        reference=reference,
                        note=form.cleaned_data.get("note"),
                    )

                    to_account.balance += amount
                    to_account.save()
                    Transaction.objects.create(
                        account=to_account,
                        transaction_type="TRANSFER_IN",
                        amount=amount,
                        balance_after=to_account.balance,
                        reference=reference,
                        note=form.cleaned_data.get("note"),
                    )
                messages.success(request, f"Transferred {amount} to {to_account.user.username}.")
                return redirect("dashboard")
    else:
        form = TransferForm()
    return render(request, "bank/transfer.html", {"form": form, "account": account})


@login_required
def transaction_history_view(request):
    account = request.user.account
    transactions = account.transactions.all()
    return render(request, "bank/transaction_history.html", {
        "account": account,
        "transactions": transactions,
    })


@login_required
def delete_account_view(request):
    if request.method == "POST":
        username = request.user.username
        user = request.user
        # Log out first, then delete: on_delete=CASCADE on Account/Transaction
        # means deleting the User wipes the bank account and its whole
        # transaction history too.
        logout(request)
        user.delete()
        messages.success(request, f"The account for '{username}' has been permanently deleted.")
        return redirect("login")
    return redirect("dashboard")
