from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, F, Q
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

User = get_user_model()


class BaseAccount(models.Model):
    ACCOUNT_TYPES = (
        ('DEBIT', 'Debit Account'),
        ('CREDIT', 'Credit Account'),
        ('SAVINGS', 'Savings Account'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)

    class Meta:
        abstract = True


class DebitAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(account_type='DEBIT')


class CreditAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(account_type='CREDIT')


class SavingsAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(account_type='SAVINGS')


class Account(BaseAccount):
    objects = models.Manager()  # Default manager
    debit = DebitAccountManager()
    credit = CreditAccountManager()
    savings = SavingsAccountManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Consolidated Account"
        verbose_name_plural = "Consolidated Accounts"

    def __str__(self):
        return f"{self.get_account_type_display()} - {self.name}"


# Proxy Models for Account Type Specialization
class DebitAccount(Account):
    class Meta:
        verbose_name = "Debit Account"
        verbose_name_plural = "Debit Accounts"

    def save(self, *args, **kwargs):
        self.account_type = 'DEBIT'
        super().save(*args, **kwargs)

    @property
    def available_balance(self):
        return self.current_balance


class CreditAccount(Account):
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_due_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Credit Account"
        verbose_name_plural = "Credit Accounts"

    def save(self, *args, **kwargs):
        self.account_type = 'CREDIT'
        super().save(*args, **kwargs)

    @property
    def available_credit(self):
        return self.credit_limit + self.current_balance  # Assuming negative balance represents used credit


class SavingsAccount(Account):
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_interest_calculation = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Savings Account"
        verbose_name_plural = "Savings Accounts"

    def save(self, *args, **kwargs):
        self.account_type = 'SAVINGS'
        super().save(*args, **kwargs)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Income'),
        ('OUT', 'Expense'),
        ('TRANSFER', 'Transfer'),
        ('CREDIT_PAYMENT', 'Credit Payment'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField()
    description = models.TextField()
    category = models.CharField(max_length=50)
    related_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='related_transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class ConsolidatedBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_balance = models.DecimalField(max_digits=12, decimal_places=2)
    debit_balance = models.DecimalField(max_digits=12, decimal_places=2)
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2)
    savings_balance = models.DecimalField(max_digits=12, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total Balance: {self.total_balance}"

    class Meta:
        verbose_name_plural = "Consolidated Balances"