from datetime import timedelta
from django.utils import timezone
from pharmacy.models import Pharmacy, Counter
from pharmacy.services import assign_prescription
from .models import Token
# tokens/services.py
from pharmacy.models import Prescription


BILLING_TIME_SEC = 180


# -----------------------------
# AUTO COMPLETE EXPIRED TOKENS
# -----------------------------
def auto_complete_expired_tokens(pharmacy):
    now = timezone.now()

    expired_tokens = Token.objects.filter(
        pharmacy=pharmacy,
        completed=False,
        counter__isnull=False,
        start_time__isnull=False,
        start_time__lte=now - timedelta(seconds=BILLING_TIME_SEC)
    )

    for token in expired_tokens:
        if token.medicine_count is None:
            print("❌ medicine_count missing for token", token.token_number)
            continue

        # 🔹 finish billing
        token.completed = True
        token.counter = None
        token.save()
        print("✅ AUTO billing finished:", token.token_number)

        # 🔹 create prescription
        prescription, created = Prescription.objects.get_or_create(
            pharmacy=token.pharmacy,
            token_number=token.token_number,
            defaults={
                "patient_name": token.patient.name,
                "medicine_count": token.medicine_count,
                "status": "WAITING"
            }
        )

        # 🔹 move waiting tokens to free counters
        assign_prescription(token.pharmacy)

    # after freeing counters, move waiting tokens
    assign_waiting_tokens(pharmacy)

# GET FREE COUNTERS
# -----------------------------
def get_free_counters(pharmacy):
    counters = Counter.objects.filter(
        pharmacy=pharmacy,
        is_active=True
    ).order_by("counter_name")

    return [
        c for c in counters
        if not Token.objects.filter(
            counter=c,
            completed=False
        ).exists()
    ]


# -----------------------------
# ASSIGN WAITING TOKENS (SAFE)
# -----------------------------
def assign_waiting_tokens(pharmacy):
    """
    Always fill ALL free counters with waiting tokens (FIFO)
    """

    while True:
        free_counters = get_free_counters(pharmacy)
        if not free_counters:
            break

        waiting_token = Token.objects.filter(
            pharmacy=pharmacy,
            completed=False,
            counter__isnull=True
        ).order_by("created_at").first()

        if not waiting_token:
            break

        counter = free_counters[0]

        waiting_token.counter = counter
        waiting_token.start_time = timezone.now()
        waiting_token.end_time = waiting_token.start_time + timedelta(
            seconds=BILLING_TIME_SEC
        )
        waiting_token.save()


# -----------------------------
# ASSIGN TOKEN
# -----------------------------
def assign_token(patient, pharmacy_id):
    pharmacy = Pharmacy.objects.get(
        pharmacy_id=pharmacy_id,
        is_active=True
    )

    auto_complete_expired_tokens(pharmacy)

    existing = Token.objects.filter(
        patient=patient,
        pharmacy=pharmacy,
        completed=False
    ).first()

    if existing:
        return existing

    last = Token.objects.filter(
        pharmacy=pharmacy
    ).order_by("-token_number").first()

    token_number = last.token_number + 1 if last else 1

    token = Token.objects.create(
        token_number=token_number,
        patient=patient,
        pharmacy=pharmacy
    )

    assign_waiting_tokens(pharmacy)
    return token


# -----------------------------
# EXPECTED TIME
# -----------------------------
def calculate_expected_time(token):
    now = timezone.now()

    if token.counter:
        return now

    active_counters = Counter.objects.filter(
        pharmacy=token.pharmacy,
        is_active=True
    ).count()

    if active_counters == 0:
        return None

    waiting_ahead = Token.objects.filter(
        pharmacy=token.pharmacy,
        completed=False,
        counter__isnull=True,
        created_at__lt=token.created_at
    ).count()

    rounds = waiting_ahead // active_counters
    return now + timedelta(seconds=(rounds + 1) * BILLING_TIME_SEC)


# -----------------------------
# MANUAL BILLING DONE (FIXED)
# -----------------------------



def billing_done(pharmacy_id, counter_name):
    print("🔥 billing_done CALLED")

    try:
        token = Token.objects.get(
            pharmacy__pharmacy_id=pharmacy_id,
            counter__counter_name=counter_name,
            completed=False
        )
    except Token.DoesNotExist:
        print("❌ Token not found")
        return None

    if token.medicine_count is None:
        print("❌ medicine_count missing")
        return None

    # ✅ FINISH BILLING
    token.completed = True
    token.counter = None
    token.save()
    print("✅ Token finished:", token.token_number)

    # ✅ CREATE PRESCRIPTION (CRITICAL)
    prescription, created = Prescription.objects.get_or_create(
        pharmacy=token.pharmacy,
        token_number=token.token_number,
        defaults={
            "patient_name": token.patient.name,
            "medicine_count": token.medicine_count,
            "status": "WAITING"
        }
    )

    # move waiting token to free counter
    assign_waiting_tokens(token.pharmacy)

    # assign to pharmacy staff
    assign_prescription(token.pharmacy)

    return token

    
# -----------------------------
# DISPLAY BOARD
# -----------------------------
def get_display_board(pharmacy_id):
    pharmacy = Pharmacy.objects.get(pharmacy_id=pharmacy_id)
        # 🔥 AUTO FINISH BILLING BEFORE DISPLAY
    auto_complete_expired_tokens(pharmacy)


    counters = Counter.objects.filter(
        pharmacy=pharmacy,
        is_active=True
    ).order_by("counter_name")

    current = {}
    for c in counters:
        t = Token.objects.filter(
            counter=c,
            completed=False
        ).first()
        current[c.counter_name.lower()] = t.token_number if t else None


    waiting = list(
        Token.objects.filter(
            pharmacy=pharmacy,
            completed=False,
            counter__isnull=True
        )
        .order_by("created_at")
        .values_list("token_number", flat=True)
    )

    return {
        "current": current,
        "waiting": waiting
    }
