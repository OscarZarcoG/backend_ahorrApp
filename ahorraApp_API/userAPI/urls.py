# userAPI/urls.py
from django.urls import path
from .views import SignUpView, LoginView, LogoutView, GetUserInfo, UpdateLastLoginView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('details/', GetUserInfo.as_view(), name='user-details'),
    path('details/<str:pk>/', GetUserInfo.as_view(), name='user-details-by-id'),
    path('update-login/<str:pk>/', UpdateLastLoginView.as_view(), name='update-last-login'),
]