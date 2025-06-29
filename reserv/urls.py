from django.urls import path

from . import views

app_name = "reserv"

urlpatterns = [
    path("", views.home, name="index"),
    path("api/tables/", views.get_tables, name="get_tables"),
    path("api/settings/", views.get_settings, name="settings_api"),
    path("book_table/", views.book_table, name="book_table"),
    path("contact/", views.contact, name="contact"),
    path("profile/", views.profile, name="profile"),
    path("cancel_booking/<int:pk>/", views.cancel_booking, name="cancel_booking"),
    # API для работы с бронированиями
    path(
        "api/reservation/<int:reservation_id>/",
        views.get_reservation,
        name="get_reservation",
    ),
    path(
        "api/reservation/<int:reservation_id>/edit/",
        views.edit_reservation,
        name="edit_reservation",
    ),
    path(
        "api/reservation/<int:reservation_id>/cancel/",
        views.cancel_reservation_api,
        name="cancel_reservation_api",
    ),
]
