from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import transaction

class Cash(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'Dólar estadounidense'),
        ('EUR', 'Euro'),
        ('MXN', 'Peso mexicano'),
    ]

    name = models.CharField(max_length=50)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TypeTransaction(models.Model):
    name = models.CharField(max_length=50)
    is_income = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    number_account = models.CharField(max_length=18, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fk_cash = models.ForeignKey(Cash, on_delete=models.PROTECT)
    fk_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number_account} - {self.fk_user.username}"

    def update_balance(self, amount):
        self.balance += amount
        self.save()


class Transaction(models.Model):
    concept = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    fk_type_transaction = models.ForeignKey(TypeTransaction, on_delete=models.CASCADE)
    fk_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    fk_category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.concept} - {self.amount}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:  # Si la transacción ya existía, revertir el balance anterior
                old_transaction = Transaction.objects.get(pk=self.pk)
                if old_transaction.fk_type_transaction.is_income:
                    old_transaction.fk_account.balance -= old_transaction.amount
                else:
                    old_transaction.fk_account.balance += old_transaction.amount
                old_transaction.fk_account.save()

            # Guardar el balance anterior antes de modificarlo
            previous_balance = self.fk_account.balance

            # Aplicar la nueva transacción
            if self.fk_type_transaction.is_income:
                self.fk_account.balance += self.amount
            else:
                if self.fk_account.balance < self.amount:
                    raise ValueError("Saldo insuficiente para realizar la transacción.")
                self.fk_account.balance -= self.amount

            self.fk_account.save()
            super().save(*args, **kwargs)

            BalanceHistory.objects.create(
                account=self.fk_account,
                transaction=self,
                previous_balance=previous_balance,
                new_balance=self.fk_account.balance
            )

class BalanceHistory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2)
    new_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historial de {self.account.number_account}"