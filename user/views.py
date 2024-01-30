from django.shortcuts import render

import os
import random
import string

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from user.form import UserRegisterForm, UserLoginForm, UserForgotPasswordForm, UserSetNewPasswordForm, \
    UserProfileForm, ModeratorUserForm, AdminUserForm
from user.models import User


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    next_page = 'mailing:mailing_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация на сайте'
        return context


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:email_confirmation_sent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        new_user = form.save()
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=60))
        new_user.email_verify_token = token
        new_user.save()
        current_site = get_current_site(self.request)
        mail_subject = 'Conrirm registration'
        message = render_to_string(
            'users/email_check.html',
            {
                'domain': current_site.domain,
                'token': token,
            },
        )
        send_mail(mail_subject, message, os.getenv('HOST_USER'), [new_user.email])
        return response


class EmailConfirmationSentView(TemplateView):
    template_name = 'users/email_confirmation_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Письмо активации отправлено'
        return context


class VerifyEmailView(View):

    def get(self, request, token):
        try:
            user = User.objects.get(email_verify_token=token)
            user.is_active = True
            user.save()
            return redirect('users:email_confirmed')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return redirect('users:email_confirmation_failed')


class EmailConfirmedView(TemplateView):
    template_name = 'users/email_confirmed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес активирован'
        return context


class EmailConfirmationFailedView(TemplateView):
    template_name = 'users/email_confirmation_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес не активирован'
        return context


class UserForgotPasswordView(PasswordResetView):
    form_class = UserForgotPasswordForm
    template_name = 'users/user_password_reset.html'
    success_url = reverse_lazy('users:password-reset-sent')
    subject_template_name = 'users/password_subject_reset_mail.txt'
    email_template_name = 'users/password_reset_mail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Запрос на сброс пароля'
        return context


class PasswordResetSentView(TemplateView):
    template_name = 'users/password_reset_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Письмо отправлено'
        return context


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = UserSetNewPasswordForm
    template_name = 'users/user_password_set_new.html'
    success_url = reverse_lazy('users:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установить новый пароль'
        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('mailing:mailing_list')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'
        return context


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    model = User
    permission_required = 'users.can_block_user'
    success_url = 'users:users_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование "{self.object}"'
        return context

    def get_success_url(self):
        return reverse('users:list_users')

    def form_valid(self, form):
        if form.is_valid():
            curr_user = User.objects.get(pk=self.get_object().pk)
            if curr_user.is_superuser:
                return HttpResponseForbidden('<h2>Нельзя блокировать суперадмина</h2>')
            else:
                return super().form_valid(form)

    def get_form_class(self):
        if self.request.user.is_superuser:
            return AdminUserForm
        elif self.request.user == self.object:
            return UserProfileForm
        return ModeratorUserForm


@login_required
@permission_required(['users.view_user'])
def get_users_list(request):
    users_list = User.objects.all()
    paginator = Paginator(users_list, 50)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'object_list': users_list,
        'title': 'Список пользователей сервиса',
        "page_obj": page_obj
    }
    return render(request, 'users/users_list.html', context)
