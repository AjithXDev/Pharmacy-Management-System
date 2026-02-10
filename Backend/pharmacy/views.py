from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.utils.timezone import localtime
from .models import Pharmacy, Prescription
from .services import assign_prescription, auto_finish_prescriptions


@api_view(["GET"])
def pharmacy_display(request, pharmacy_id):
    try:
        pharmacy = Pharmacy.objects.get(
            pharmacy_id=pharmacy_id,
            is_active=True
        )
    except Pharmacy.DoesNotExist:
        return Response({"error": "Invalid pharmacy"}, status=404)

    auto_finish_prescriptions(pharmacy)
    assign_prescription(pharmacy)

    preparing = Prescription.objects.filter(
        pharmacy=pharmacy,
        status="PREPARING"
    )

    waiting_count = Prescription.objects.filter(
        pharmacy=pharmacy,
        status="WAITING"
    ).count()

    return Response({
        "pharmacy_id": pharmacy_id,
        "preparing": [
            {
                "token": p.token_number,
                "staff": p.assigned_staff.name if p.assigned_staff else None,
                "medicine_count": p.medicine_count,
                "started_at": localtime(p.start_time).strftime("%I:%M %p") if p.start_time else None,
                "expected_ready_time": localtime(p.end_time).strftime("%I:%M %p") if p.end_time else None,

                "time_remaining": (
    max(
        0,
        int((p.end_time - timezone.now()).total_seconds())
    )
    if p.end_time else 0
)
            }
            for p in preparing
        ],
        "waiting_count": waiting_count
    })


@api_view(["GET"])
def user_expected_time(request, token_number):
    pharmacy_id = request.query_params.get("pharmacy_id")

    try:
        p = Prescription.objects.get(
            pharmacy__pharmacy_id=pharmacy_id,
            token_number=token_number,
            status__in=["WAITING", "PREPARING"]
        )
    except Prescription.DoesNotExist:
        return Response({"error": "Token not found"}, status=404)

    if not p.start_time or not p.end_time:
        return Response({"error": "Prescription not started"}, status=400)

    total = (p.end_time - p.start_time).total_seconds()
    elapsed = (timezone.now() - p.start_time).total_seconds()
    progress = min(100, max(0, (elapsed / total) * 100))

    return Response({
        "token": token_number,
        "status": p.status,
        "medicine_count": p.medicine_count,
        "expected_ready_time": localtime(p.end_time).strftime("%I:%M %p"),
        "progress_percent": round(progress, 1)
    })


@api_view(["POST"])
def finish_prescription(request, token_number):
    pharmacy_id = request.data.get("pharmacy_id")

    try:
        p = Prescription.objects.get(
            pharmacy__pharmacy_id=pharmacy_id,
            token_number=token_number,
            status="PREPARING"
        )
    except Prescription.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    staff = p.assigned_staff

    p.status = "DONE"
    p.assigned_staff = None
    p.save()

    if staff:
        staff.is_busy = False
        staff.save()

    assign_prescription(p.pharmacy)

    return Response({
        "message": f"Token {token_number} completed manually"
    })


@api_view(["GET"])
def prescription_status(request, token_number):
    pharmacy_id = request.query_params.get("pharmacy_id")

    try:
        p = Prescription.objects.get(
            pharmacy__pharmacy_id=pharmacy_id,
            token_number=token_number
        )
    except Prescription.DoesNotExist:
        return Response({"error": "Prescription not found"}, status=404)

    return Response({
        "token": p.token_number,
        "status": p.status,
        "staff": p.assigned_staff.name if p.assigned_staff else None,
        "started_at": localtime(p.start_time).strftime("%I:%M %p") if p.start_time else None,
        "expected_ready_time": localtime(p.end_time).strftime("%I:%M %p") if p.end_time else None,

    })
