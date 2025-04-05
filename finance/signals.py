from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=Transaction)
@receiver(post_delete, sender=Transaction)
def update_balances(sender, instance, **kwargs):
    def update_account(account, amount, operation):
        if operation in ['IN', 'CREDIT_PAYMENT']:
            account.current_balance += amount
        elif operation in ['OUT', 'TRANSFER']:
            account.current_balance -= amount
        account.save()

    # Handle transaction operations
    if instance.transaction_type == 'TRANSFER':
        update_account(instance.account, instance.amount, 'OUT')
        update_account(instance.related_account, instance.amount, 'IN')
    elif instance.transaction_type == 'CREDIT_PAYMENT':
        update_account(instance.account, instance.amount, 'IN')
        if instance.related_account:  # Link to debit account payment
            update_account(instance.related_account, instance.amount, 'OUT')
    else:
        update_account(instance.account, instance.amount, instance.transaction_type)

    # Update consolidated balance
    user_accounts = Account.objects.filter(user=instance.user)
    ConsolidatedBalance.objects.update_or_create(
        user=instance.user,
        defaults={
            'total_balance': user_accounts.aggregate(total=Sum('current_balance'))['total'] or 0,
            'debit_balance': user_accounts.debit.aggregate(total=Sum('current_balance'))['total'] or 0,
            'credit_balance': user_accounts.credit.aggregate(total=Sum('current_balance'))['total'] or 0,
            'savings_balance': user_accounts.savings.aggregate(total=Sum('current_balance'))['total'] or 0,
        }
    )