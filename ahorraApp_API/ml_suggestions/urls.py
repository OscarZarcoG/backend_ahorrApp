from django.urls import path
from .views import UserSuggestionsView

urlpatterns = [
    path('suggestions/<str:number_account>/', UserSuggestionsView.as_view(), name='user-suggestions'),
]