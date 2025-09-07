from django.urls import path
from . import views

app_name = 'streams'

urlpatterns = [
    path('', views.MyStreamLinksView.as_view(), name='list'),
    path('add/', views.StreamLinkCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.StreamLinkUpdateView.as_view(), name='edit'),
    path('<int:pk>/toggle/', views.StreamLinkToggleActiveView.as_view(), name='toggle'),
]

