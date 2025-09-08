from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View, DetailView
from django.shortcuts import get_object_or_404, render

from .models import StreamLink, Clip, Profile, StreamRating, ClipRating
from django.db.models import Count, Q
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
            .annotate(
                clip_count=Count('clips'),
                up_count=Count('stream_ratings', filter=Q(stream_ratings__value=1)),
                down_count=Count('stream_ratings', filter=Q(stream_ratings__value=-1)),
            )
        )


class PublicStreamDetailView(DetailView):
    model = StreamLink
    template_name = 'streams/public_detail.html'
    context_object_name = 'stream'

    def get_queryset(self):
        # annotate up/down counts for the stream
        return (
            super().get_queryset()
            .annotate(
                up_count=Count('stream_ratings', filter=Q(stream_ratings__value=1)),
                down_count=Count('stream_ratings', filter=Q(stream_ratings__value=-1)),
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['clips'] = (
            self.object.clips
            .select_related('submitter')
            .annotate(
                up_count=Count('clip_ratings', filter=Q(clip_ratings__value=1)),
                down_count=Count('clip_ratings', filter=Q(clip_ratings__value=-1)),
            )
        )
        ctx['form'] = ClipForm()
        if self.request.user.is_authenticated:
            sr = StreamRating.objects.filter(stream=self.object, user=self.request.user).first()
            ctx['my_stream_vote'] = sr.value if sr else 0
            # Build dict of clip_id -> vote value
            user_votes = {
                cr.clip_id: cr.value for cr in ClipRating.objects.filter(user=self.request.user, clip__stream=self.object)
            }
            ctx['my_clip_votes'] = user_votes
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


class MyClipsView(LoginRequiredMixin, ListView):
    model = Clip
    template_name = 'streams/clip_list.html'
    context_object_name = 'clips'

    def get_queryset(self):
        return (
            Clip.objects.filter(submitter=self.request.user)
            .select_related('stream', 'submitter')
        )


class ClipUpdateView(LoginRequiredMixin, UpdateView):
    model = Clip
    form_class = ClipForm
    template_name = 'streams/clip_form.html'
    success_url = reverse_lazy('streams:my_clips')

    def get_queryset(self):
        return Clip.objects.filter(submitter=self.request.user)


class PublicProfileView(View):
    template_name = 'streams/public_profile.html'

    def get(self, request, user_id: int):
        user = get_object_or_404(self.model_user(), pk=user_id)
        profile, _ = Profile.objects.get_or_create(user=user)
        return render(request, self.template_name, {
            'user_obj': user,
            'profile': profile,
        })

    @staticmethod
    def model_user():
        from django.contrib.auth import get_user_model
        return get_user_model()


class RateStreamView(LoginRequiredMixin, View):
    def post(self, request, pk):
        stream = get_object_or_404(StreamLink, pk=pk)
        try:
            value = int(request.POST.get('value'))
        except (TypeError, ValueError):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        if value not in (1, -1):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        obj, created = StreamRating.objects.get_or_create(stream=stream, user=request.user, defaults={'value': value})
        if not created:
            if obj.value == value:
                obj.delete()  # toggle off
            else:
                obj.value = value
                obj.save(update_fields=['value'])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class RateClipView(LoginRequiredMixin, View):
    def post(self, request, pk):
        clip = get_object_or_404(Clip, pk=pk)
        try:
            value = int(request.POST.get('value'))
        except (TypeError, ValueError):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        if value not in (1, -1):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        obj, created = ClipRating.objects.get_or_create(clip=clip, user=request.user, defaults={'value': value})
        if not created:
            if obj.value == value:
                obj.delete()
            else:
                obj.value = value
                obj.save(update_fields=['value'])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
