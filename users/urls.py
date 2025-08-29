from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, home_view, login_view, register_view, logout_view,
    profile_view, users_list_view, settings_view, change_password_view
)

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Template-based views
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('list/', users_list_view, name='list'),
    path('settings/', settings_view, name='settings'),
    path('change-password/', change_password_view, name='change_password'),
]
