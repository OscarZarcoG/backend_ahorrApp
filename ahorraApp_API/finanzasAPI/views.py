from rest_framework import viewsets, status, serializers, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Cash, TypeTransaction, Category, Account, Transaction, BalanceHistory
from .serializers import CashSerializer, TypeTransactionSerializer, CategorySerializer, AccountSerializer, \
    TransactionSerializer, BalanceHistorySerializer


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
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(fk_user=self.request.user)

    def perform_create(self, serializer):
        if Account.objects.filter(fk_user=self.request.user).exists():
            raise serializers.ValidationError("No puedes crear más de una cuenta por usuario")
        serializer.save(fk_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(fk_user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(fk_account__fk_user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            account_id = request.data.get('fk_account')
            if not Account.objects.filter(id=account_id, fk_user=request.user).exists():
                return Response(
                    {"error": "No tienes permiso para realizar transacciones en esta cuenta"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except:
            return Response(
                {"error": "Cuenta inválida"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.fk_account.fk_user != request.user:
            return Response(
                {"error": "No tienes permiso para modificar esta transacción"},
                status=status.HTTP_403_FORBIDDEN
            )

        account_id = request.data.get('fk_account')
        if account_id and not Account.objects.filter(id=account_id, fk_user=request.user).exists():
            return Response(
                {"error": "No tienes permiso para realizar transacciones en esta cuenta"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)


class BalanceHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = BalanceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BalanceHistory.objects.filter(account__fk_user=self.request.user)


