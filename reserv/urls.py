from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("reserve/", views.create_reservation, name="reserve"),
]
