from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from pharmacy.models import Pharmacy, Counter
from patients.models import Patient
from .models import Token

from .services import (
    assign_token,
    billing_done,
    get_display_board,
    calculate_expected_time,
    assign_waiting_tokens
)


@api_view(["POST"])
def generate_token_api(request, pharmacy_id):
    patient_id = request.data.get("patient_id")

    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)

    token = assign_token(patient, pharmacy_id)
    token.refresh_from_db()

    expected = calculate_expected_time(token)

    return Response({
        "token": token.token_number,
        "generated_expected_time": (
            timezone.localtime(expected).strftime("%H:%M")
            if expected else None
        )
    })


@api_view(["GET"])
def display_board_api(request, pharmacy_id):
    return Response(get_display_board(pharmacy_id))



@api_view(["POST"])
def manual_billing_done_api(request):
    pharmacy_id = request.data.get("pharmacy_id")
    counter_name = request.data.get("counter")

    token = billing_done(pharmacy_id, counter_name)

    if not token:
        return Response({"error": "billing failed"}, status=400)

    return Response({
        "token": token.token_number,
        "medicine_count": token.medicine_count
    })

@api_view(["POST"])
def add_counter_api(request, pharmacy_id):
    pharmacy = Pharmacy.objects.get(pharmacy_id=pharmacy_id)

    count = pharmacy.counters.count() + 1
    name = f"C{count}"

    Counter.objects.create(
        pharmacy=pharmacy,
        counter_name=name,
        is_active=True
    )

    assign_waiting_tokens(pharmacy)

    return Response({
        "message": "Counter added",
        "counter": name
    })


@api_view(["GET"])
def token_time_api(request, pharmacy_id, token_number):
    try:
        token = Token.objects.get(
            pharmacy__pharmacy_id=pharmacy_id,
            token_number=token_number,
            completed=False
        )
    except Token.DoesNotExist:
        return Response({"error": "Token not found"}, status=404)

    expected = calculate_expected_time(token)

    return Response({
        "token": token_number,
        "current_expected_time": (
            timezone.localtime(expected).strftime("%H:%M")
            if expected else None
        )
    })

@api_view(["POST"])
def set_medicine_count_api(request):
    token_number = request.data.get("token")
    medicine_count = request.data.get("medicine_count")

    if token_number is None or medicine_count is None:
        return Response(
            {"error": "token and medicine_count required"},
            status=400
        )

    try:
        token = Token.objects.get(
            token_number=token_number,
            completed=False
        )
    except Token.DoesNotExist:
        return Response(
            {"error": "Active token not found"},
            status=404
        )

    token.medicine_count = int(medicine_count)
    token.save()

    # ✅ EXACT RESPONSE YOU WANT
    return Response({
        "token": token.token_number,
        "medicine_count": token.medicine_count
    })