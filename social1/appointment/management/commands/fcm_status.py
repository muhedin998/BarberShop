from django.core.management.base import BaseCommand
from appointment.models import Korisnik, FCMToken

class Command(BaseCommand):
    help = 'Check FCM token status for users'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Check specific username (optional)')
        parser.add_argument('--all', action='store_true', help='Show all users with FCM tokens')

    def handle(self, *args, **options):
        if options['username']:
            # Check specific user
            try:
                user = Korisnik.objects.get(username=options['username'])
                self.show_user_tokens(user)
            except Korisnik.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{options["username"]}" not found')
                )
        elif options['all']:
            # Show all users with tokens
            users_with_tokens = Korisnik.objects.filter(fcmtoken__isnull=False).distinct()
            self.stdout.write(f"Found {users_with_tokens.count()} users with FCM tokens:")
            self.stdout.write("-" * 50)
            
            for user in users_with_tokens:
                self.show_user_tokens(user)
                self.stdout.write("-" * 30)
        else:
            # Show summary
            total_users = Korisnik.objects.count()
            users_with_tokens = Korisnik.objects.filter(fcmtoken__isnull=False).distinct().count()
            total_tokens = FCMToken.objects.count()
            active_tokens = FCMToken.objects.filter(is_active=True).count()
            
            self.stdout.write("FCM Token Summary:")
            self.stdout.write(f"Total users: {total_users}")
            self.stdout.write(f"Users with FCM tokens: {users_with_tokens}")
            self.stdout.write(f"Total FCM tokens: {total_tokens}")
            self.stdout.write(f"Active FCM tokens: {active_tokens}")
            
            self.stdout.write("\nUse --all to see all users or --username <username> for specific user")

    def show_user_tokens(self, user):
        tokens = FCMToken.objects.filter(user=user)
        active_tokens = tokens.filter(is_active=True)
        
        self.stdout.write(f"User: {user.username} ({user.email})")
        self.stdout.write(f"  Total tokens: {tokens.count()}")
        self.stdout.write(f"  Active tokens: {active_tokens.count()}")
        
        for token in tokens:
            status = "ACTIVE" if token.is_active else "INACTIVE"
            self.stdout.write(f"  - Token ID: {token.id}")
            self.stdout.write(f"    Device: {token.device_id}")
            self.stdout.write(f"    Status: {status}")
            self.stdout.write(f"    Created: {token.created_at}")
            self.stdout.write(f"    Updated: {token.updated_at}")
            self.stdout.write(f"    Token: {token.token[:50]}..." if len(token.token) > 50 else f"    Token: {token.token}")