from django.urls import path
from . import views

app_name = 'streams'

urlpatterns = [
    path('', views.MyStreamLinksView.as_view(), name='list'),
    path('add/', views.StreamLinkCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.StreamLinkUpdateView.as_view(), name='edit'),
    path('<int:pk>/toggle/', views.StreamLinkToggleActiveView.as_view(), name='toggle'),
    path('<int:pk>/finish/', views.StreamLinkToggleFinishedView.as_view(), name='toggle_finished'),
    # Public detail page for a stream
    path('<int:pk>/', views.PublicStreamDetailView.as_view(), name='public_detail'),
    # My clips
    path('clips/', views.MyClipsView.as_view(), name='my_clips'),
    path('clips/<int:pk>/edit/', views.ClipUpdateView.as_view(), name='clip_edit'),
    # Public user profile
    path('user/<int:user_id>/', views.PublicProfileView.as_view(), name='user_profile'),
    # Ratings
    path('rate/stream/<int:pk>/', views.RateStreamView.as_view(), name='rate_stream'),
    path('rate/clip/<int:pk>/', views.RateClipView.as_view(), name='rate_clip'),
]
