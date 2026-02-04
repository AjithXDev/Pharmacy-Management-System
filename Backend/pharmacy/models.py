from django.db import models

class Pharmacy(models.Model):
    pharmacy_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Counter(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        related_name="counters",
        on_delete=models.CASCADE
    )
    counter_name = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("pharmacy", "counter_name")

class PharmacyStaff(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        related_name="staff",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_busy = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Prescription(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)  # NOT NULL
    token_number = models.IntegerField()
    patient_name = models.CharField(max_length=100)
    medicine_count = models.IntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=[
            ("WAITING", "Waiting"),
            ("PREPARING", "Preparing"),
            ("DONE", "Done"),
        ],
        default="WAITING"
    )

    assigned_staff = models.ForeignKey(
        PharmacyStaff,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("pharmacy", "token_number")
