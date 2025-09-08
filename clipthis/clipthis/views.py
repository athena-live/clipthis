from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from streams.forms import ProfileForm
from streams.models import Profile, BillingTransaction, StreamLink
from django.conf import settings
from django.contrib import messages

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
        # Reconcile any pending Stripe transactions (in case user didn't hit success URL)
        if stripe and getattr(settings, 'STRIPE_SECRET_KEY', ''):
            try:
                pending = BillingTransaction.objects.filter(user=user, status=BillingTransaction.STATUS_PENDING).order_by('-created_at')[:3]
                if pending:
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    for txn in pending:
                        if not txn.stripe_session_id:
                            continue
                        try:
                            sess = stripe.checkout.Session.retrieve(txn.stripe_session_id)
                            pay_status = getattr(sess, 'payment_status', None)
                            if pay_status == 'paid':
                                txn.status = BillingTransaction.STATUS_PAID
                                txn.stripe_payment_intent = getattr(sess, 'payment_intent', '') or ''
                                txn.save(update_fields=['status', 'stripe_payment_intent'])
                                profile.plan = txn.plan
                                profile.save(update_fields=['plan'])
                                messages.success(request, f'Your plan has been upgraded to {txn.plan}.')
                                break
                        except Exception:
                            continue
            except Exception:
                pass
        user_form = self._user_form(instance=user)
        profile_form = ProfileForm(instance=profile)
        used = StreamLink.objects.filter(owner=user).count()
        limit = Profile.plan_limit(profile.plan)
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "profile": profile,
                "plan_limit": limit,
                "plan_used": used,
            },
        )

    def post(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        user_form = self._user_form(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(self.success_url)
        used = StreamLink.objects.filter(owner=user).count()
        limit = Profile.plan_limit(profile.plan)
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "profile": profile,
                "plan_limit": limit,
                "plan_used": used,
            },
        )

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
            messages.error(request, 'Invalid plan selected.')
            return redirect('pricing')
        profile, _ = Profile.objects.get_or_create(user=request.user)
        # Free plan immediate
        if plan == 'free':
            profile.plan = plan
            profile.save(update_fields=['plan'])
            messages.success(request, 'You are now on the Free plan.')
            return redirect('profile')
        # For paid plans, create a checkout session if stripe available
        if not getattr(settings, 'STRIPE_SECRET_KEY', '') or not stripe:
            messages.error(request, 'Payments are not configured. Please try again later or contact support.')
            return redirect('pricing')
        if stripe and getattr(settings, 'STRIPE_SECRET_KEY', ''):
            stripe.api_key = settings.STRIPE_SECRET_KEY
            price_map = {
                'plus': 9_99,      # in cents
                'premium': 14_99,  # in cents
            }
            amount = price_map.get(plan)
            if not amount:
                messages.error(request, 'Invalid price for selected plan.')
                return redirect('pricing')
            try:
                # Record pending transaction
                txn = BillingTransaction.objects.create(
                    user=request.user,
                    plan=plan,
                    amount_cents=amount,
                    currency='usd',
                    status=BillingTransaction.STATUS_PENDING,
                )
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
                    success_url=request.build_absolute_uri('/billing/success/?plan=' + plan + '&session_id={CHECKOUT_SESSION_ID}'),
                    cancel_url=request.build_absolute_uri('/billing/cancel/'),
                    customer_email=request.user.email or None,
                    metadata={'user_id': str(request.user.id), 'plan': plan, 'txn_id': str(txn.id)},
                )
                # Save session id on txn
                txn.stripe_session_id = session.id
                txn.save(update_fields=['stripe_session_id'])
                return redirect(session.url)
            except Exception as e:
                messages.error(request, f'Unable to start checkout: {e}')
                return redirect('pricing')


class BillingSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        plan = request.GET.get('plan')
        session_id = request.GET.get('session_id')
        if plan in ('plus', 'premium') and stripe and getattr(settings, 'STRIPE_SECRET_KEY', '') and session_id:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                session = stripe.checkout.Session.retrieve(session_id)
                payment_intent = getattr(session, 'payment_intent', None)
                payment_status = getattr(session, 'payment_status', None)
                # Update transaction
                txn = BillingTransaction.objects.filter(user=request.user, stripe_session_id=session_id).first()
                if txn:
                    # Fallback to payment_intent status if payment_status not present
                    status = BillingTransaction.STATUS_FAILED
                    if payment_status == 'paid':
                        status = BillingTransaction.STATUS_PAID
                    elif payment_intent:
                        try:
                            pi = stripe.PaymentIntent.retrieve(payment_intent)
                            if getattr(pi, 'status', '') in ('succeeded', 'requires_capture'):
                                status = BillingTransaction.STATUS_PAID
                        except Exception:
                            pass
                    txn.status = status
                    txn.stripe_payment_intent = payment_intent or ''
                    txn.save(update_fields=['status', 'stripe_payment_intent'])
                # Apply plan if paid
                if payment_status == 'paid' or (txn and txn.status == BillingTransaction.STATUS_PAID):
                    profile, _ = Profile.objects.get_or_create(user=request.user)
                    profile.plan = plan
                    profile.save(update_fields=['plan'])
                    messages.success(request, f'Your plan has been upgraded to {plan}.')
                    return redirect('profile')
            except Exception:
                pass
        # Default: show success page; user can navigate to profile
        return render(request, 'billing/success.html', {'plan': plan})


class BillingCancelView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'billing/cancel.html')
