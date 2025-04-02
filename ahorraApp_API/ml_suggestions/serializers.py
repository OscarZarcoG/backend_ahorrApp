from rest_framework import serializers
from .models import Suggestion


class SuggestionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='fk_category.name', read_only=True)

    class Meta:
        model = Suggestion
        fields = ['id', 'fk_category', 'category_name', 'message', 'severity', 'created_at']