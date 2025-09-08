from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView


class ProfileView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    fields = ["first_name", "last_name"]
    template_name = "account/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user

