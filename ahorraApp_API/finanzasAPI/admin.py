from django.contrib import admin
from .models import Cash, TypeTransaction, Category, Account, Transaction, BalanceHistory

admin.site.register(Cash)
admin.site.register(TypeTransaction)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(BalanceHistory)
