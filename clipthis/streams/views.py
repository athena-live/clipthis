from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View, DetailView

from .models import StreamLink, Clip
from django.db.models import Count
from .forms import StreamLinkForm, ClipForm


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


class PublicActiveLinksView(ListView):
    model = StreamLink
    template_name = 'home.html'
    context_object_name = 'active_links'

    def get_queryset(self):
        return (
            StreamLink.objects
            .filter(active=True)
            .select_related('owner')
            .annotate(clip_count=Count('clips'))
        )


class PublicStreamDetailView(DetailView):
    model = StreamLink
    template_name = 'streams/public_detail.html'
    context_object_name = 'stream'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['clips'] = self.object.clips.select_related('submitter')
        ctx['form'] = ClipForm()
        return ctx

    def post(self, request, *args, **kwargs):
        # Allow authenticated users to submit a clip
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('account_login'))
        form = ClipForm(request.POST)
        if form.is_valid():
            clip = form.save(commit=False)
            clip.stream = self.object
            clip.submitter = request.user
            clip.save()
            return HttpResponseRedirect(self.request.path)
        ctx = self.get_context_data(object=self.object)
        ctx['form'] = form
        return self.render_to_response(ctx)
