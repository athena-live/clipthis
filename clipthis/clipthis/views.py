from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from streams.forms import ProfileForm
from streams.models import Profile
from django.conf import settings

try:
    import stripe  # type: ignore
except Exception:
    stripe = None


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
        # Simple dynamic ModelForm for first/last name only with Bootstrap widgets
        from django import forms
        User = get_user_model()

        class _F(forms.ModelForm):
            class Meta:
                model = User
                fields = ["first_name", "last_name"]
                widgets = {
                    "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
                    "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
                }

        return _F(*args, **kwargs)


class PricingView(LoginRequiredMixin, View):
    template_name = "billing/pricing.html"

    def get(self, request):
        return render(request, self.template_name, {
            'stripe_pk': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
        })


class SelectPlanView(LoginRequiredMixin, View):
    def post(self, request, plan):
        if plan not in ('free', 'plus', 'premium'):
            return redirect('pricing')
        profile, _ = Profile.objects.get_or_create(user=request.user)
        # Free plan immediate
        if plan == 'free' or not getattr(settings, 'STRIPE_SECRET_KEY', ''):
            profile.plan = plan
            profile.save(update_fields=['plan'])
            return redirect('profile')
        # For paid plans, create a checkout session if stripe available
        if stripe and getattr(settings, 'STRIPE_SECRET_KEY', ''):
            stripe.api_key = settings.STRIPE_SECRET_KEY
            price_map = {
                'plus': 9_99,      # in cents
                'premium': 14_99,  # in cents
            }
            amount = price_map.get(plan)
            if not amount:
                return redirect('pricing')
            try:
                session = stripe.checkout.Session.create(
                    mode='payment',
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {'name': f'ClipThis {plan.capitalize()} Plan'},
                            'unit_amount': amount,
                        },
                        'quantity': 1,
                    }],
                    success_url=request.build_absolute_uri('/billing/success/?plan=' + plan),
                    cancel_url=request.build_absolute_uri('/billing/cancel/'),
                    customer_email=request.user.email or None,
                )
                return redirect(session.url)
            except Exception:
                # Fallback: set plan directly if Stripe fails
                profile.plan = plan
                profile.save(update_fields=['plan'])
                return redirect('profile')
        # Without stripe module, set directly
        profile.plan = plan
        profile.save(update_fields=['plan'])
        return redirect('profile')


class BillingSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        plan = request.GET.get('plan')
        if plan in ('free', 'plus', 'premium'):
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.plan = plan
            profile.save(update_fields=['plan'])
        return render(request, 'billing/success.html', {'plan': plan})


class BillingCancelView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'billing/cancel.html')
