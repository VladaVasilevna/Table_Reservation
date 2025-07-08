from django.contrib import admin

from .models import ContactMessage, Reservation, Settings, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity", "shape", "is_active")
    list_filter = ("shape", "is_active")
    search_fields = ("number",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "table",
        "formatted_date",
        "formatted_time",
        "duration_hours",
        "end_time",
        "guests",
        "status",
        "formatted_created_at",
    )
    list_filter = ("status", "date", "table", "duration_hours")
    search_fields = ("name", "email", "user__username")
    readonly_fields = ("formatted_created_at", "end_time")
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("user", "table", "name", "email", "phone")},
        ),
        (
            "Детали бронирования",
            {
                "fields": (
                    "date",
                    "time",
                    "duration_hours",
                    "end_time",
                    "guests",
                    "status",
                )
            },
        ),
        ("Дополнительно", {"fields": ("comment", "formatted_created_at")}),
    )

    def formatted_date(self, obj):
        return obj.date.strftime("%d.%m.%Y")

    formatted_date.short_description = "Дата"

    def formatted_time(self, obj):
        return obj.time.strftime("%H:%M")

    formatted_time.short_description = "Время"

    def formatted_created_at(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")

    formatted_created_at.short_description = "Дата создания"

    def end_time(self, obj):
        """Отобразить время окончания брони"""
        end_time = obj.get_actual_end_time()
        return (
            end_time.strftime("%H:%M")
            if hasattr(end_time, "strftime")
            else str(end_time)
        )

    end_time.short_description = "Время окончания"


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = (
        "booking_duration_hours",
        "formatted_open_time",
        "formatted_close_time",
        "formatted_last_booking",
    )

    def formatted_open_time(self, obj):
        return obj.restaurant_open_time.strftime("%H:%M")

    formatted_open_time.short_description = "Время открытия"

    def formatted_close_time(self, obj):
        return obj.restaurant_close_time.strftime("%H:%M")

    formatted_close_time.short_description = "Время закрытия"

    def formatted_last_booking(self, obj):
        return obj.last_booking_time.strftime("%H:%M")

    formatted_last_booking.short_description = "Последнее время брони"

    def has_add_permission(self, request):
        # Разрешаем создать только один объект настроек
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удалять настройки
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "formatted_created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("formatted_created_at",)
    list_editable = ("is_read",)

    def formatted_created_at(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")

    formatted_created_at.short_description = "Дата создания"

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Отметить как прочитанные"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    mark_as_unread.short_description = "Отметить как непрочитанные"

    actions = [mark_as_read, mark_as_unread]
