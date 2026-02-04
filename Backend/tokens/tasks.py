from celery import shared_task
from pharmacy.models import Pharmacy
from tokens.services import assign_waiting_tokens


@shared_task
def auto_assign_waiting_tokens():
    total = 0
    for pharmacy in Pharmacy.objects.filter(is_active=True):
        before = pharmacy.token_set.filter(
            completed=False,
            counter__isnull=True
        ).count()

        assign_waiting_tokens(pharmacy)

        after = pharmacy.token_set.filter(
            completed=False,
            counter__isnull=True
        ).count()

        total += max(0, before - after)

    return f"Auto-assigned {total} tokens"
