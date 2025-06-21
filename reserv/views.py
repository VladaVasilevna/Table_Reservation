from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from config import settings

from .forms import BookingForm, ContactForm, ModalBookingForm
from .models import Reservation, Settings, Table


def home(request):
    booking_form = BookingForm()
    modal_form = ModalBookingForm()
    contact_form = ContactForm()

    # Обработка формы обратной связи
    if request.method == "POST" and "contact_submit" in request.POST:
        print(f"Contact form POST data: {request.POST}")  # Отладочная информация
        contact_form = ContactForm(request.POST)
        print(
            f"Contact form is valid: {contact_form.is_valid()}"
        )  # Отладочная информация

        if not contact_form.is_valid():
            print(
                f"Contact form errors: {contact_form.errors}"
            )  # Отладочная информация

        if contact_form.is_valid():
            # Сохраняем сообщение в базу данных
            contact_message = contact_form.save(commit=False)
            contact_message.save()
            print(
                f"Contact message saved with ID: {contact_message.id}"
            )  # Отладочная информация

            # Отправляем email администратору
            name = contact_form.cleaned_data["name"]
            email = contact_form.cleaned_data["email"]
            subject = contact_form.cleaned_data["subject"]
            message = contact_form.cleaned_data["message"]

            admin_message = f"""
            Новое сообщение с сайта:
            Имя: {name}
            Email: {email}
            Тема: {subject}
            Сообщение: {message}
            """

            try:
                send_mail(
                    f"Новое сообщение с сайта: {subject}",
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],  # Отправляем администратору
                    fail_silently=True,  # Не показываем ошибки отправки пользователю
                )
                print("Email sent successfully")  # Отладочная информация
            except Exception as e:
                print(f"Ошибка отправки email: {e}")

            messages.success(
                request,
                "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.",
            )
            contact_form = ContactForm()  # Очищаем форму
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")

    return render(
        request,
        "reserv/index.html",
        {
            "booking_form": booking_form,
            "modal_form": modal_form,
            "contact_form": contact_form,
        },
    )


def get_settings(request):
    """API для получения настроек системы"""
    try:
        settings = Settings.get_settings()
        return JsonResponse(
            {
                "booking_duration_hours": settings.booking_duration_hours,
                "restaurant_open_time": settings.restaurant_open_time.strftime("%H:%M"),
                "restaurant_close_time": settings.restaurant_close_time.strftime(
                    "%H:%M"
                ),
                "last_booking_time": settings.last_booking_time.strftime("%H:%M"),
            }
        )
    except Exception as e:
        print(f"Error in get_settings: {e}")  # Отладочная информация
        # Возвращаем значения по умолчанию в случае ошибки
        return JsonResponse(
            {
                "booking_duration_hours": 2,
                "restaurant_open_time": "11:00",
                "restaurant_close_time": "23:00",
                "last_booking_time": "22:00",
            }
        )


def get_tables(request):
    date = request.GET.get("date")
    time = request.GET.get("time")

    # Получаем все брони на указанную дату
    reservations = Reservation.objects.filter(
        date=date,
        status__in=["pending", "confirmed"],  # Учитываем только активные брони
    )

    # Создаем список забронированных столов для указанного времени
    reserved_tables = set()

    for reservation in reservations:
        # Вычисляем время окончания брони из индивидуальной продолжительности
        start_time = datetime.strptime(str(reservation.time), "%H:%M:%S").time()
        start_datetime = datetime.combine(reservation.date, start_time)
        end_datetime = start_datetime + timedelta(hours=reservation.duration_hours)

        # Получаем настройки для проверки времени закрытия
        system_settings = Settings.get_settings()

        # Если бронь заканчивается после времени закрытия, то она заканчивается в момент закрытия
        close_datetime = datetime.combine(
            reservation.date, system_settings.restaurant_close_time
        )

        if end_datetime > close_datetime:
            end_datetime = close_datetime

        end_time = end_datetime.time()

        # Проверяем, попадает ли запрашиваемое время в интервал брони
        requested_time = datetime.strptime(time, "%H:%M").time()

        if start_time <= requested_time < end_time:
            reserved_tables.add(reservation.table_id)

    qs = Table.objects.filter(is_active=True)
    tables = [
        {
            "id": t.id,
            "number": t.number,
            "shape": t.shape,
            "x": t.x,
            "y": t.y,
            "width": t.width,
            "height": t.height,
            "capacity": t.capacity,
            "reserved": t.id in reserved_tables,
        }
        for t in qs
    ]
    return JsonResponse({"tables": tables})


@login_required
def book_table(request):
    if request.method == "POST":
        booking_form = ModalBookingForm(request.POST)
        print(f"POST data: {request.POST}")  # Отладочная информация
        print(f"Form is valid: {booking_form.is_valid()}")  # Отладочная информация

        if not booking_form.is_valid():
            print(f"Form errors: {booking_form.errors}")  # Отладочная информация

        if booking_form.is_valid():
            # Проверяем, не существует ли уже бронирование на этот стол в это время
            table_id = request.POST.get("table_id")
            date = booking_form.cleaned_data["date"]
            time = booking_form.cleaned_data["time"]

            # Получаем настройки для расчета времени окончания брони
            system_settings = Settings.get_settings()

            # Вычисляем время окончания брони
            start_time = datetime.strptime(str(time), "%H:%M:%S").time()
            start_datetime = datetime.combine(date, start_time)
            end_datetime = start_datetime + timedelta(
                hours=system_settings.booking_duration_hours
            )

            # Если бронь заканчивается после времени закрытия, то она заканчивается в момент закрытия
            close_datetime = datetime.combine(
                date, system_settings.restaurant_close_time
            )
            if end_datetime > close_datetime:
                end_datetime = close_datetime

            end_time = end_datetime.time()

            # Проверяем конфликты с существующими бронированиями
            conflicting_reservations = Reservation.objects.filter(
                table_id=table_id,
                date=date,
                status__in=["pending", "confirmed"],
                time__lt=end_time,
            )

            # Проверяем, что время начала новой брони не меньше времени окончания существующих
            for reservation in conflicting_reservations:
                reservation_start = datetime.strptime(
                    str(reservation.time), "%H:%M:%S"
                ).time()
                reservation_start_datetime = datetime.combine(
                    reservation.date, reservation_start
                )
                reservation_end_datetime = reservation_start_datetime + timedelta(
                    hours=reservation.duration_hours
                )

                # Если бронь заканчивается после времени закрытия, то она заканчивается в момент закрытия
                if reservation_end_datetime > close_datetime:
                    reservation_end_datetime = close_datetime

                reservation_end = reservation_end_datetime.time()

                # Проверяем пересечение интервалов
                if start_time < reservation_end and reservation_start < end_time:
                    error_message = (
                        f"Стол уже забронирован на это время. "
                        f"Существующая бронь: {reservation.time} - {reservation_end}"
                    )
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse(
                            {"success": False, "errors": {"__all__": [error_message]}},
                            status=400,
                        )
                    else:
                        messages.error(request, error_message)
                        return redirect("home")

            r = booking_form.save(commit=False)
            r.user = request.user
            r.table = get_object_or_404(Table, id=table_id)
            r.status = "pending"
            # Устанавливаем продолжительность брони из настроек по умолчанию
            r.duration_hours = system_settings.booking_duration_hours
            r.save()
            send_mail(
                f"Бронь #{r.id} от Savor",
                f"Добрый день, {r.name}!\n"
                f"Вы забронировали столик №{r.table.number} на {r.guests} персон.\n"
                f"Дата брони: {r.date.strftime('%d.%m.%Y')}\n"
                f"Время брони: {r.time.strftime('%H:%M') if hasattr(r.time, 'strftime') else str(r.time)}\n"
                f"Продолжительность брони: 2 часа.\n"
                f"В ближайшее время наш администратор свяжется с Вами для подтверждения брони и уточнения деталей.\n"
                f"Спасибо, что выбрали наш ресторан!",
                settings.DEFAULT_FROM_EMAIL,
                [r.email],
            )
            messages.success(request, "Бронь успешно создана!")

            # Проверяем, является ли это AJAX запросом
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Бронирование успешно создано!",
                        "redirect_url": "/",
                    }
                )
            else:
                return redirect("home")
        else:
            # Если форма невалидна
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "errors": booking_form.errors}, status=400
                )
            else:
                messages.error(request, "Ошибка при создании бронирования.")
                return redirect("home")
    return redirect("home")


@login_required
def profile(request):
    reservations = Reservation.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "reserv/profile.html", {"reservations": reservations})


@login_required
def cancel_booking(request, pk):
    r = get_object_or_404(Reservation, pk=pk, user=request.user)
    r.status = "canceled"
    r.save()
    return redirect("profile")


# API endpoints для работы с бронированиями
@login_required
def get_reservation(request, reservation_id):
    """API для получения данных бронирования"""
    try:
        reservation = get_object_or_404(
            Reservation, id=reservation_id, user=request.user
        )
        time_str = (
            reservation.time.strftime("%H:%M")
            if hasattr(reservation.time, "strftime")
            else str(reservation.time)
        )
        return JsonResponse(
            {
                "id": reservation.id,
                "date": reservation.date.strftime("%Y-%m-%d"),
                "time": time_str,
                "guests": reservation.guests,
                "duration_hours": reservation.duration_hours,
                "comment": reservation.comment,
                "table_number": reservation.table.number,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def edit_reservation(request, reservation_id):
    """API для редактирования бронирования"""
    if request.method != "POST":
        return JsonResponse({"error": "Метод не поддерживается"}, status=405)

    try:
        reservation = get_object_or_404(
            Reservation, id=reservation_id, user=request.user
        )

        # Получаем данные из формы
        date = request.POST.get("date")
        time = request.POST.get("time")
        guests = request.POST.get("guests")
        duration_hours = request.POST.get("duration_hours")
        comment = request.POST.get("comment", "")

        # Валидация данных
        if not all([date, time, guests, duration_hours]):
            return JsonResponse(
                {"error": "Все поля обязательны для заполнения"}, status=400
            )

        # Проверяем, что выбранная дата не в прошлом
        from datetime import datetime

        selected_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        if selected_datetime < datetime.now():
            return JsonResponse(
                {"error": "Нельзя бронировать на прошедшее время"}, status=400
            )

        # Получаем настройки для проверки времени работы ресторана
        system_settings = Settings.get_settings()

        # Проверяем время работы ресторана
        time_obj = datetime.strptime(time, "%H:%M").time()
        if (
            time_obj < system_settings.restaurant_open_time
            or time_obj >= system_settings.restaurant_close_time
        ):
            return JsonResponse(
                {
                    "error": (
                        f"Ресторан работает с {system_settings.restaurant_open_time} "
                        f"до {system_settings.restaurant_close_time}"
                    )
                },
                status=400,
            )

        # Проверяем, что бронь не выходит за пределы работы ресторана
        from datetime import datetime

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        start_datetime = datetime.combine(date_obj, time_obj)
        end_datetime = start_datetime + timedelta(hours=int(duration_hours))
        close_datetime = datetime.combine(
            date_obj, system_settings.restaurant_close_time
        )

        if end_datetime > close_datetime:
            return JsonResponse(
                {
                    "error": (
                        f"Бронирование не может заканчиваться после "
                        f"{system_settings.restaurant_close_time}"
                    )
                },
                status=400,
            )

        # Проверяем конфликты с другими бронированиями (исключая текущее)
        conflicting_reservations = Reservation.objects.filter(
            table=reservation.table, date=date, status__in=["pending", "confirmed"]
        ).exclude(id=reservation.id)

        for other_reservation in conflicting_reservations:
            other_start = datetime.strptime(
                str(other_reservation.time), "%H:%M:%S"
            ).time()
            other_start_datetime = datetime.combine(other_reservation.date, other_start)
            other_end_datetime = other_start_datetime + timedelta(
                hours=other_reservation.duration_hours
            )

            if other_end_datetime > close_datetime:
                other_end_datetime = close_datetime

            other_end = other_end_datetime.time()

            # Проверяем пересечение интервалов
            if time_obj < other_end and other_start < time_obj:
                return JsonResponse(
                    {
                        "error": (
                            f"Стол уже забронирован на это время. "
                            f"Существующая бронь: {other_reservation.time} - {other_end}"
                        )
                    },
                    status=400,
                )

        # Сохраняем изменения
        reservation.date = date_obj
        reservation.time = time_obj
        reservation.guests = guests
        reservation.duration_hours = duration_hours
        reservation.comment = comment
        reservation.save()

        # Отправляем email об изменении бронирования
        send_mail(
            f"Изменение брони #{reservation.id} от Savor",
            f"Добрый день, {reservation.name}!\n"
            f"Ваше бронирование было изменено:\n"
            f"Столик №{reservation.table.number}\n"
            f"Дата: {reservation.date.strftime('%d.%m.%Y')}\n"
            f"Время: {time_obj.strftime('%H:%M')}\n"
            f"Количество гостей: {reservation.guests}\n"
            f"Продолжительность: {reservation.duration_hours} часа\n"
            f"Комментарий: {reservation.comment or 'Не указан'}\n"
            f"Спасибо, что выбрали наш ресторан!",
            settings.DEFAULT_FROM_EMAIL,
            [reservation.email],
        )

        return JsonResponse(
            {"success": True, "message": "Бронирование успешно изменено"}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def cancel_reservation_api(request, reservation_id):
    """API для отмены бронирования"""
    if request.method != "POST":
        return JsonResponse({"error": "Метод не поддерживается"}, status=405)

    try:
        reservation = get_object_or_404(
            Reservation, id=reservation_id, user=request.user
        )

        # Отменяем бронирование
        reservation.status = "canceled"
        reservation.save()

        # Отправляем email об отмене
        time_str = (
            reservation.time.strftime("%H:%M")
            if hasattr(reservation.time, "strftime")
            else str(reservation.time)
        )
        send_mail(
            f"Отмена брони #{reservation.id} от Savor",
            f"Ваше бронирование на {reservation.date.strftime('%d.%m.%Y')} {time_str} отменено!\n"
            f"Если это не Вы отменили бронирование, пожалуйста, свяжитесь с нами по телефону +7 900 000 00 00.",
            settings.DEFAULT_FROM_EMAIL,
            [reservation.email],
        )

        return JsonResponse({"success": True, "message": "Бронирование отменено"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
