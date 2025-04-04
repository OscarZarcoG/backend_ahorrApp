from .models import Cash, TypeTransaction, Category, Account, Transaction, BalanceHistory
from rest_framework import serializers

class CashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cash
        fields = ['name', 'currency', 'created_at', 'updated_at']

class TypeTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTransaction
        fields = ['name', 'is_income']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'status']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['number_account', 'balance', 'fk_cash', 'fk_user', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['concept', 'amount', 'fk_type_transaction', 'fk_account', 'fk_category', 'created_at', 'updated_at']

class BalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceHistory
        fields = ['account', 'transaction', 'previous_balance', 'new_balance', 'created_at']