import logging
import secrets

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserLoginForm, UserProfileForm, UserRegisterForm
from users.models import User

logger = logging.getLogger(__name__)


def login_view(request):
    """Кастомное представление для входа с использованием email"""
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("reserv:index")
            else:
                form.add_error(None, "Неверный email или пароль.")
    else:
        form = UserLoginForm()

    return render(request, "users/registration/login.html", {"form": form})


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                self.object.is_active = False
                self.object.token = secrets.token_hex(16)
                self.object.save()
                host = self.request.get_host()
                url = f"http://{host}/users/email-confirm/{self.object.token}/"
                send_mail(
                    subject="Подтверждение почты",
                    message=f"Привет! Перейди по ссылке для подтверждения почты {url}",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[self.object.email],
                )
                return response
        except Exception:
            form.add_error(None, "Ошибка отправки письма. Попробуйте позже.")
            return self.form_invalid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = None
    user.save()
    return redirect(reverse("users:login"))


def manager_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == "manager")(
        view_func
    )


@manager_required
def user_list(request):
    users = User.objects.all()
    return render(request, "users/user_list.html", {"users": users})


@manager_required
def block_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()
    return redirect("users:user_list")


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем бронирования пользователя
        from reserv.models import Reservation

        context["reservations"] = Reservation.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user

    def get_form_class(self):
        logger.info("Используемая форма: %s", self.form_class)
        return super().get_form_class()


@login_required
def delete_profile(request):
    """API для удаления профиля пользователя"""
    if request.method != "POST":
        return JsonResponse({"error": "Метод не поддерживается"}, status=405)

    try:
        user = request.user

        # Проверяем, есть ли активные бронирования
        from reserv.models import Reservation

        active_reservations = Reservation.objects.filter(
            user=user, status__in=["pending", "confirmed"]
        ).count()

        if active_reservations > 0:
            return JsonResponse(
                {
                    "error": (
                        f"Нельзя удалить профиль с активными бронированиями "
                        f"({active_reservations} шт.). Сначала отмените все бронирования."
                    )
                },
                status=400,
            )

        # Удаляем пользователя
        user.delete()

        return JsonResponse(
            {"success": True, "message": "Профиль успешно удален", "redirect_url": "/"}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
