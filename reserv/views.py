from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import BookingForm, ContactForm
from django.contrib import messages

def home(request):
    booking_form = BookingForm()
    contact_form = ContactForm()

    if request.method == 'POST':
        # Определяем, какая форма была отправлена по имени кнопки submit или скрытому полю
        if 'booking_submit' in request.POST:
            booking_form = BookingForm(request.POST)
            if booking_form.is_valid():
                send_mail(
                    'Новое бронирование',
                    f"Детали бронирования:\n{booking_form.cleaned_data}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Ваш запрос на бронирование успешно отправлен! Мы свяжемся с вами в ближайшее время. Спасибо, что выбрали Savor!')
                return redirect('home')
        elif 'contact_submit' in request.POST:
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                send_mail(
                    contact_form.cleaned_data['subject'],
                    contact_form.cleaned_data['message'],
                    contact_form.cleaned_data['email'],
                    [settings.DEFAULT_FROM_EMAIL],
                )
                messages.success(request, 'Ваше сообщение успешно отправлено! Спасибо за обратную связь.')
                return redirect('home')

    return render(request, 'reserv/index.html', {
        'booking_form': booking_form,
        'contact_form': contact_form,
    })
