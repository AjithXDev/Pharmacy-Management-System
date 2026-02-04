from datetime import timedelta
from django.utils import timezone
from ml.predict import predict_prescription_time
from .models import PharmacyStaff, Prescription


def assign_prescription(pharmacy):
    free_staff = PharmacyStaff.objects.filter(
        pharmacy=pharmacy,
        is_active=True,
        is_busy=False
    ).order_by("id")

    waiting = Prescription.objects.filter(
        pharmacy=pharmacy,
        status="WAITING"
    ).order_by("created_at")

    for staff, prescription in zip(free_staff, waiting):
        total_seconds = predict_prescription_time(
            prescription.medicine_count
        )

        prescription.status = "PREPARING"
        prescription.assigned_staff = staff
        prescription.start_time = timezone.now()
        prescription.end_time = prescription.start_time + timedelta(seconds=total_seconds)
        prescription.save()

        staff.is_busy = True
        staff.save()

def auto_finish_prescriptions(pharmacy):
    """
    Auto-complete prescriptions whose end_time has passed
    """

    now = timezone.now()

    preparing = Prescription.objects.filter(
        pharmacy=pharmacy,
        status="PREPARING",
        end_time__isnull=False
    )

    for p in preparing:
        if now >= p.end_time:
            staff = p.assigned_staff

            p.status = "DONE"
            p.assigned_staff = None
            p.save()

            if staff:
                staff.is_busy = False
                staff.save()

    # After finishing, try assigning again
    assign_prescription(pharmacy)
