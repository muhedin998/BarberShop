from django.core.management.base import BaseCommand
from appointment.models import Korisnik, Notification, FCMToken

class Command(BaseCommand):
    help = 'Test push notification system by creating a test notification'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to send test notification to')
        parser.add_argument('--title', type=str, default='Test Notification', help='Notification title')
        parser.add_argument('--message', type=str, default='This is a test push notification from Django!', help='Notification message')

    def handle(self, *args, **options):
        username = options['username']
        title = options['title']
        message = options['message']

        try:
            # Get the user
            user = Korisnik.objects.get(username=username)
            self.stdout.write(f"Found user: {user.username}")

            # Check if user has FCM tokens
            tokens = FCMToken.objects.filter(user=user, is_active=True)
            self.stdout.write(f"User has {tokens.count()} active FCM tokens")
            
            for token in tokens:
                self.stdout.write(f"  - Token ID: {token.id}, Device: {token.device_id}")

            # Create a test notification
            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message
            )

            self.stdout.write(
                self.style.SUCCESS(f'Test notification created with ID: {notification.id}')
            )
            self.stdout.write(f'Push notification should be sent automatically...')
            
            # Check if push was sent
            notification.refresh_from_db()
            if notification.push_sent:
                self.stdout.write(self.style.SUCCESS('Push notification was sent successfully!'))
            else:
                self.stdout.write(self.style.WARNING('Push notification was not sent. Check logs for details.'))

        except Korisnik.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )