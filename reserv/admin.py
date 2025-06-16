from django.contrib import admin

from .models import Reservation, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity", "is_active")
    list_editable = ("is_active",)
    search_fields = ("number",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "table", "date", "time", "status")
    list_filter = ("status", "date")
    search_fields = ("user__username", "table__number")
