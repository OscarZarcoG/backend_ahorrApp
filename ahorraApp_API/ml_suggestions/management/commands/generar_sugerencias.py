from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from finanzasAPI.models import Account
from ml_suggestions.models import Suggestion


class Command(BaseCommand):
    help = 'Genera sugerencias usando inteligencia artificial'

    def handle(self, *args, **options):
        accounts = Account.objects.filter(
            transaction__created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).distinct()

        total_suggestions = 0

        for account in accounts:
            try:
                suggestions = Suggestion.generate_suggestions(account)
                count = len(suggestions)
                total_suggestions += count
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {count} sugerencias para cuenta {account.number_account}')
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f'✗ Error en cuenta {account.number_account}: {str(e)}'))

        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 Total sugerencias generadas: {total_suggestions}'))