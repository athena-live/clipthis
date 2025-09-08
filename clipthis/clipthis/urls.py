"""
URL configuration for clipthis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from streams.views import PublicActiveLinksView
from django.contrib.auth.decorators import login_required
from .views import ProfileView, PricingView, SelectPlanView, BillingSuccessView, BillingCancelView, ThemeToggleView

urlpatterns = [
    path('', PublicActiveLinksView.as_view(), name='home'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('streams/', include('streams.urls', namespace='streams')),
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('billing/select/<str:plan>/', SelectPlanView.as_view(), name='billing_select'),
    path('billing/success/', BillingSuccessView.as_view(), name='billing_success'),
    path('billing/cancel/', BillingCancelView.as_view(), name='billing_cancel'),
    path('settings/theme/', ThemeToggleView.as_view(), name='theme_toggle'),
    path('terms/', TemplateView.as_view(template_name='legal/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy'),
    path('copyright/', TemplateView.as_view(template_name='legal/copyright.html'), name='copyright'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
]
