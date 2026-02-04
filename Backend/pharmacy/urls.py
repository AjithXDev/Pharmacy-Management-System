from django.urls import path
from .views import (
    finish_prescription,
    pharmacy_display,
    user_expected_time,
    prescription_status
)

urlpatterns = [
    path("<str:pharmacy_id>/display/", pharmacy_display),
    path("finish/<int:token_number>/", finish_prescription),
    path(
        "token/<int:token_number>/expected-time/",
        user_expected_time
    ),
    path(
        "prescription/<int:token_number>/status/",
        prescription_status
    ),
]
