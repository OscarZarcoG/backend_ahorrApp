from django.core.management.base import BaseCommand
from finanzasAPI.models import Account
from ml_suggestions.models import Suggestion


class Command(BaseCommand):
    help = 'Genera sugerencias personalizadas para todos los usuarios basadas en sus patrones de gasto'

    def handle(self, *args, **options):
        accounts = Account.objects.all()

        for account in accounts:
            try:
                suggestions = Suggestion.generate_suggestions(account)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Generadas {len(suggestions)} sugerencias para la cuenta {account.number_account}'
                    )
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f'✗ Error al generar sugerencias para la cuenta {account.number_account}: {str(e)}'
                    )
                )