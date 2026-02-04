from celery import shared_task
from .models import Pharmacy
from .services import auto_finish_prescriptions


@shared_task
def auto_finish_all_pharmacies():
    for pharmacy in Pharmacy.objects.filter(is_active=True):
        auto_finish_prescriptions(pharmacy)
