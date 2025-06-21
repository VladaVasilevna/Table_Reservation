from django.contrib import admin

# Глобальные настройки админки
admin.site.site_header = "Администрирование ресторана Savor"
admin.site.site_title = "Savor Admin"
admin.site.index_title = "Панель управления"

# Настройки форматирования дат для админки
admin.site.enable_nav_sidebar = True


# Функция для форматирования дат в админке
def format_date_for_admin(date_obj):
    """Форматирует дату в формате DD.MM.YYYY для админки"""
    if hasattr(date_obj, "strftime"):
        return date_obj.strftime("%d.%m.%Y")
    return str(date_obj)


def format_datetime_for_admin(datetime_obj):
    """Форматирует дату и время в формате DD.MM.YYYY HH:MM для админки"""
    if hasattr(datetime_obj, "strftime"):
        return datetime_obj.strftime("%d.%m.%Y %H:%M")
    return str(datetime_obj)
