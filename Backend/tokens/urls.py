from django.urls import path
from .views import (
    generate_token_api,
    display_board_api,
    manual_billing_done_api,
    add_counter_api,
    token_time_api,
    set_medicine_count_api
)

urlpatterns = [
    # 🔹 Generate token (initial expected time)
    path("<str:pharmacy_id>/generate/", generate_token_api),

    # 🔹 Display board (current + waiting)
    path("<str:pharmacy_id>/display/", display_board_api),

    # 🔹 Manual billing done (free counter)
    path("billing-done/", manual_billing_done_api),

    # 🔹 Add new counter
    path("<str:pharmacy_id>/add-counter/", add_counter_api),

    # 🔹 Check updated expected time for a token
    path(
        "<str:pharmacy_id>/token-time/<int:token_number>/",
        token_time_api
    ),
    path("set-medicine-count/", set_medicine_count_api),

]
