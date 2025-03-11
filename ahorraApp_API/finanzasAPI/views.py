from rest_framework import viewsets
from .models import Cash, TypeTransaction, Category, Account, Transaction, BalanceHistory
from .serializers import CashSerializer, TypeTransactionSerializer, CategorySerializer, AccountSerializer, TransactionSerializer, BalanceHistorySerializer

class CashViewSet(viewsets.ModelViewSet):
    queryset = Cash.objects.all()
    serializer_class = CashSerializer

class TypeTransactionViewSet(viewsets.ModelViewSet):
    queryset = TypeTransaction.objects.all()
    serializer_class = TypeTransactionSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(fk_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(fk_user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class BalanceHistoryViewSet(viewsets.ModelViewSet):
    queryset = BalanceHistory.objects.all()
    serializer_class = BalanceHistorySerializer