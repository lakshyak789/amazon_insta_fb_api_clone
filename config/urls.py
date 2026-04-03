from django.contrib import admin
from django.urls import path, include
from core.views_auth import RegisterView, LoginView, LogoutView, RefreshView, MeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/auth/register', RegisterView.as_view(), name='auth-register'),
    path('v1/auth/login', LoginView.as_view(), name='auth-login'),
    path('v1/auth/logout', LogoutView.as_view(), name='auth-logout'),
    path('v1/auth/refresh', RefreshView.as_view(), name='auth-refresh'),
    path('v1/me', MeView.as_view(), name='me'),
    path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.jwt')),
    path('v1/amazon/', include('amazon.urls')),
    path('v1/facebook/', include('facebook.urls')),
    path('v1/instagram/', include('instagram.urls')),
]
