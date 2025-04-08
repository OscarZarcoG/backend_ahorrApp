from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CashViewSet, TypeTransactionViewSet, CategoryViewSet, AccountViewSet, TransactionViewSet, BalanceHistoryViewSet

router = DefaultRouter()
router.register(r'cash', CashViewSet)
router.register(r'type-transaction', TypeTransactionViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'account', AccountViewSet, basename='account')
router.register(r'transaction', TransactionViewSet, basename='transaction')
router.register(r'balance-history', BalanceHistoryViewSet, basename='balance-history')

urlpatterns = [
    path('', include(router.urls)),
]
