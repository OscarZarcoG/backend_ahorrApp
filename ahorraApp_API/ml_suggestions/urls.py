from django.urls import path
from .views import UserSuggestionsView

urlpatterns = [
    path(
        'accounts/<str:account_number>/suggestions/',
        UserSuggestionsView.as_view(),
        name='user-suggestions'
    ),
]