from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/tables/", views.get_tables, name="get_tables"),
    path("api/settings/", views.get_settings, name="get_settings"),
    path("book_table/", views.book_table, name="book_table"),
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
