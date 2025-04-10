from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Suggestion
from .serializers import SuggestionSerializer
from finanzasAPI.models import Account
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum


class UserSuggestionsView(generics.ListAPIView):
    serializer_class = SuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_object_or_404(
            Account,
            fk_user=self.request.user,
            number_account=self.kwargs['number_account']
        )
        return Suggestion.objects.filter(
            fk_account=account,
            is_active=True
        ).select_related('fk_category').order_by('-severity', '-created_at')

    def list(self, request, *args, **kwargs):
        account = get_object_or_404(
            Account,
            fk_user=request.user,
            number_account=kwargs['number_account']
        )

        return Response({
            'suggestions': self.get_serializer(self.get_queryset(), many=True).data,
            'stats': self.get_financial_stats(account),
            'model_metadata': self.get_model_metadata()  # Nuevo: info del modelo
        })

    def get_model_metadata(self):
        model_path = settings.BASE_DIR / 'Backend_ahorrApp' / 'ahorraApp_API' / 'ml_suggestions' / 'ml_models' / 'category_classifier.pkl'
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
        return {
            'accuracy': data['metadata']['accuracy'],
            'last_trained': data['metadata']['last_trained']
        }