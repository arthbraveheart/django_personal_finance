from django.contrib import admin
from .models import (
    Account, DebitAccount, CreditAccount, SavingsAccount,
    Transaction, ConsolidatedBalance
)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account_type', 'current_balance', 'created_at')
    list_filter = ('account_type', 'user')
    search_fields = ('name', 'user__username')
    readonly_fields = ('account_type', 'created_at')

    def has_add_permission(self, request):
        """Prevent direct creation of base Account instances"""
        return False


@admin.register(DebitAccount)
class DebitAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'current_balance', 'created_at')
    list_filter = ('user',)
    search_fields = ('name', 'user__username')
    readonly_fields = ('account_type', 'created_at')

    def get_queryset(self, request):
        return self.model.objects.filter(account_type='DEBIT')


@admin.register(CreditAccount)
class CreditAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'current_balance', 'credit_limit', 'payment_due_date')
    list_filter = ('user', 'payment_due_date')
    search_fields = ('name', 'user__username')
    fields = ('user', 'name', 'credit_limit', 'payment_due_date', 'current_balance')
    readonly_fields = ('current_balance', 'created_at')


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'current_balance', 'interest_rate', 'last_interest_calculation')
    list_filter = ('user', 'interest_rate')
    search_fields = ('name', 'user__username')
    fields = ('user', 'name', 'interest_rate', 'last_interest_calculation', 'current_balance')
    readonly_fields = ('current_balance', 'created_at')


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fk_name = 'account'
    readonly_fields = ('created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'account', 'transaction_type', 'amount', 'category')
    list_filter = ('account','transaction_type', 'category', 'date')
    search_fields = ('description', 'account__name')
    raw_id_fields = ('account', 'related_account')
    date_hierarchy = 'date'


@admin.register(ConsolidatedBalance)
class ConsolidatedBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_balance', 'debit_balance', 'credit_balance',
                    'savings_balance', 'last_updated')
    readonly_fields = ('last_updated',)

    def has_add_permission(self, request):
        """Balances are auto-generated, no manual creation"""
        return False