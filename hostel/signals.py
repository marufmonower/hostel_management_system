from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Income, Expenditure


@receiver(post_save, sender=Payment)
def associate_payment(sender, instance, created, **kwargs):
    if created and instance.status == 'Completed':

        # print(f"instance_status{instance.status.lower()}")

        if 'completed' in instance.status.lower():
            Income.objects.create(amount=instance, category='Rent')
        else:
            Expenditure.objects.create(
                date=instance.payment_date,  # Set the date from Payment
                amount=instance.amount,  # Use the amount from Payment
                category='Miscellaneous'  # Default category
            )
    if created:
        print(f"Signal triggered for Payment ID: {instance.id}")
