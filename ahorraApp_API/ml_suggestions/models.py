from django.db import models
from finanzasAPI.models import Account, Category, Transaction, BalanceHistory
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
import os
import pickle
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import LabelEncoder
import json
from django.conf import settings


class Suggestion(models.Model):
    fk_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    fk_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=20, null=True, choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta')
    ])
    amount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Sugerencia para {self.fk_account} - {self.fk_category}"

    @classmethod
    def generate_suggestions(cls, account):
        model_path = settings.BASE_DIR / 'ml_suggestions' / 'ml_models' / 'category_classifier.pkl'
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        model = model_data['model']

        last_month = timezone.now() - timedelta(days=30)
        transactions = Transaction.objects.filter(
            fk_account=account,
            created_at__gte=last_month
        )

        X = pd.DataFrame([{
            'amount': t.amount,
            'fk_type_transaction': t.fk_type_transaction.id,
            'hora_dia': t.hora_dia,
            'dia_semana': t.dia_semana,
            'mes': t.mes
        } for t in transactions])

        predicted_categories = model.predict(X)

        # Aquí puedes agregar lógica para generar sugerencias basadas en:
        # - Comparar categorías reales vs predichas
        # - Patrones de gasto
        # - Otras reglas de negocio

        suggestions = []
        for idx, t in enumerate(transactions):
            if t.fk_category.name != predicted_categories[idx]:
                suggestions.append(
                    Suggestion(
                        fk_account=account,
                        fk_category=t.fk_category,
                        message=f"Posible categoría incorrecta. El modelo sugiere: {predicted_categories[idx]}",
                        severity='medium'
                    )
                )

        cls.objects.bulk_create(suggestions)
        return suggestions