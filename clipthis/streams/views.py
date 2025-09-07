from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View

from .models import StreamLink
from .forms import StreamLinkForm


class MyStreamLinksView(LoginRequiredMixin, ListView):
    model = StreamLink
    template_name = 'streams/link_list.html'
    context_object_name = 'links'

    def get_queryset(self):
        return StreamLink.objects.filter(owner=self.request.user)


class StreamLinkCreateView(LoginRequiredMixin, CreateView):
    model = StreamLink
    form_class = StreamLinkForm
    template_name = 'streams/link_form.html'
    success_url = reverse_lazy('streams:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class StreamLinkUpdateView(LoginRequiredMixin, UpdateView):
    model = StreamLink
    form_class = StreamLinkForm
    template_name = 'streams/link_form.html'
    success_url = reverse_lazy('streams:list')

    def get_queryset(self):
        return StreamLink.objects.filter(owner=self.request.user)


class StreamLinkToggleActiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        link = StreamLink.objects.filter(owner=request.user, pk=pk).first()
        if link:
            link.active = not link.active
            link.save(update_fields=['active'])
        return HttpResponseRedirect(reverse_lazy('streams:list'))

