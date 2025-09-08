from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from streams.forms import ProfileForm
from streams.models import Profile


class ProfileView(LoginRequiredMixin, View):
    template_name = "account/profile.html"
    success_url = reverse_lazy("profile")

    class UserForm(get_user_model()._meta.default_manager.model._meta.model.__class__):
        pass

    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        user_form = self._user_form(instance=user)
        profile_form = ProfileForm(instance=profile)
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})

    def post(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        user_form = self._user_form(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})

    def _user_form(self, *args, **kwargs):
        # Simple dynamic ModelForm for first/last name only
        from django import forms
        User = get_user_model()

        class _F(forms.ModelForm):
            class Meta:
                model = User
                fields = ["first_name", "last_name"]

        return _F(*args, **kwargs)
