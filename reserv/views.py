from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from config import settings
from .forms import BookingForm, ContactForm, RegistrationForm
from .models import Reservation, Table


def home(request):
    booking_form = BookingForm()
    contact_form = ContactForm()
    return render(request, "reserv/index.html", {"booking_form": booking_form})


def get_tables(request):
    date = request.GET.get("date")
    time = request.GET.get("time")
    reserved = Reservation.objects.filter(date=date, time=time).values_list(
        "table_id", flat=True
    )
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
            "reserved": t.id in reserved,
        }
        for t in qs
    ]
    return JsonResponse({"tables": tables})


@login_required
def book_table(request):
    if request.method == "POST":
        booking_form = BookingForm(request.POST)
        if booking_form.is_valid():
            r = booking_form.save(commit=False)
            r.user = request.user
            r.table = get_object_or_404(Table, id=request.POST.get("table_id"))
            r.status = "pending"
            r.save()
            send_mail(
                "Бронирование от Savor",
                f"Добрый день, {r.name}!"
                f"Вы забронировали столик №{r.table.number} на {r.date} {r.time} на {r.guests} персон."
                f"В ближайшее время наш администратор свяжется с Вами для подтверждения брони и уточнения деталей."
                f"Спасибо, что выбрали наш ресторан!",
                settings.DEFAULT_FROM_EMAIL,
                [r.email],
            )
            messages.success(request, "Бронь успешно создана!")
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
