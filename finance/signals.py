from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import *


def update_account(account, amount, operation, reverse=False):
    multiplier = -1 if reverse else 1

    if operation in ['IN', 'CREDIT_PAYMENT']:
        account.current_balance += multiplier * amount
    elif operation in ['OUT', 'TRANSFER']:
        account.current_balance -= multiplier * amount
    account.save()

    user_accounts = Account
    person = account.user
    ConsolidatedBalance.objects.update_or_create(
        user= person,
        defaults={
            'total_balance': user_accounts.objects.filter(user=person).aggregate(total=Sum('current_balance'))[
                                 'total'] or 0,
            'debit_balance': user_accounts.debit.filter(user=person).aggregate(total=Sum('current_balance'))[
                                 'total'] or 0,
            'credit_balance': user_accounts.credit.filter(user=person).aggregate(total=Sum('current_balance'))[
                                  'total'] or 0,
            'savings_balance': user_accounts.savings.filter(user=person).aggregate(total=Sum('current_balance'))[
                                   'total'] or 0,
        }
    )

@receiver(post_save, sender=Transaction)
def update_balances(sender, instance, **kwargs):

    # Handle transaction operations
    if instance.transaction_type == 'TRANSFER':
        update_account(instance.account, instance.amount, 'OUT')
        update_account(instance.related_account, instance.amount, 'IN') ####
    elif instance.transaction_type == 'CREDIT_PAYMENT':
        update_account(instance.account, instance.amount, 'IN')
        if instance.related_account:  # Link to debit account payment
            update_account(instance.related_account, instance.amount, 'OUT')
    else:
        update_account(instance.account, instance.amount, instance.transaction_type)


@receiver(post_delete, sender=Transaction)
def update_balances(sender, instance, **kwargs):

    # Handle transaction operations
    if instance.transaction_type == 'TRANSFER':
        update_account(instance.account, instance.amount, 'OUT', reverse=True)
        update_account(instance.related_account, instance.amount, 'IN', reverse=True) ####
    elif instance.transaction_type == 'CREDIT_PAYMENT':
        update_account(instance.account, instance.amount, 'IN', reverse=True)
        if instance.related_account:  # Link to debit account payment
            update_account(instance.related_account, instance.amount, 'OUT', reverse=True)
    else:
        update_account(instance.account, instance.amount, instance.transaction_type, reverse=True)

