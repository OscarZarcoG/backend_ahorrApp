from django.urls import path
from .views import UserSuggestionsView

urlpatterns = [
    path(
        'accounts/<str:account_id>/suggestions/',
        UserSuggestionsView.as_view(),
        name='user-suggestions'
    ),
]