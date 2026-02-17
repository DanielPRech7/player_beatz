from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


class BaseView(PermissionRequiredMixin, SuccessMessageMixin, View):
    raise_exception = True
    permission_required = []

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseView, self).dispatch(request, *args, **kwargs)



class BaseListView(BaseView, ListView):
    paginate_by = 15


class BaseCreateView(BaseView, CreateView):
    pass


class BaseUpdateView(BaseView, UpdateView):
    pass


class BaseDeleteView(BaseView, DeleteView):
    template_name = 'core/components/delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)

        return super(BaseDeleteView, self).delete(request, *args, **kwargs)


class BaseDetailView(BaseView, DetailView):
    def get_object(self):
        return get_object_or_404(self.model.objects.all(), pk=self.kwargs.get('pk'))