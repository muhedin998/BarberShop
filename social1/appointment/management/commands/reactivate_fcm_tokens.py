from django.core.management.base import BaseCommand
from appointment.models import FCMToken

class Command(BaseCommand):
    help = 'Reactivate all FCM tokens for testing'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Reactivate tokens for specific user only')

    def handle(self, *args, **options):
        if options['username']:
            # Reactivate tokens for specific user
            tokens = FCMToken.objects.filter(user__username=options['username'])
        else:
            # Reactivate all tokens
            tokens = FCMToken.objects.all()

        updated = tokens.update(is_active=True)
        
        self.stdout.write(
            self.style.SUCCESS(f'Reactivated {updated} FCM tokens')
        )
        
        if options['username']:
            self.stdout.write(f'Tokens reactivated for user: {options["username"]}')
        else:
            self.stdout.write('All FCM tokens reactivated')