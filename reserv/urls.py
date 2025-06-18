from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('api/tables/', views.get_tables, name='get_tables'),
    path('book/', views.book_table, name='book_table'),
    path('profile/', views.profile, name='profile'),
    path('profile/cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),
]
