from django.contrib import admin
from .models import Pharmacy, Counter, PharmacyStaff, Prescription

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("pharmacy_id", "name", "is_active")


@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ("pharmacy", "counter_name", "is_active")

@admin.register(PharmacyStaff)
class PharmacyStaffAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "is_busy")
    list_filter = ("is_active", "is_busy")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("token_number", "status", "assigned_staff", "created_at")
    list_filter = ("status",)