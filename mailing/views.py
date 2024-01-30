from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.forms import inlineformset_factory
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from mailing.form import MailingForm, MailingSettingsForm
from mailing.models import Message, Mailing


class GetUserForFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingListView(LoginRequiredMixin, ListView):
    paginate_by = 50
    model = Message
    template_name = 'mailing/mailing_list.html'
    extra_context = {'title': 'Список рассылок'}

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('mailing.view_mailingmessage'):
            return queryset.order_by('pk')
        else:
            return queryset.filter(owner=self.request.user).order_by('-pk')


class MailingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/mailing_details.html'
    permission_required = 'mailing.view_mailingmessage'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = Mailing.objects.filter(message_id=self.kwargs.get('pk'))
        return context

    def has_permission(self):
        obj = self.get_object()
        return obj.owner == self.request.user or super().has_permission()

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для просмотра")


class MailingCreateView(LoginRequiredMixin, GetUserForFormMixin, CreateView):
    model = Message
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm
    success_url = reverse_lazy('mailing:mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание рассылки'
        formset_factory = inlineformset_factory(Message, Mailing, form=MailingSettingsForm,
                                                extra=1, can_delete=False)
        if self.request.method == 'POST':
            context['formset'] = formset_factory(self.request.POST, )
        else:
            context['formset'] = formset_factory()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            self.object.owner = self.request.user
            self.object.save()

            formset.instance = self.object
            for f in formset:
                start_time = f.cleaned_data.get('start_time')
                finish_time = f.cleaned_data.get('finish_time')
                if start_time is not None:
                    if start_time < datetime.now().date():
                        form.add_error(None, "Неправильная дата рассылки")
                        return self.form_invalid(form=form)
                    elif start_time > finish_time:
                        form.add_error(None, "Дата начала рассылки должна быть меньше даты её окончания")
                        return self.form_invalid(form=form)
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, GetUserForFormMixin, UpdateView):
    model = Message
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm
    success_url = reverse_lazy('mailing:mailing_list')

class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    template_name = 'mailing/mailing_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_superuser or obj.owner == self.request.user