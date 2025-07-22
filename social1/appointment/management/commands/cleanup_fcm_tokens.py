from django.core.management.base import BaseCommand
from appointment.models import FCMToken

class Command(BaseCommand):
    help = 'Clean up duplicate and old FCM tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', 
            action='store_true',
            help='Show what would be cleaned up without actually doing it'
        )
        parser.add_argument(
            '--keep-per-user',
            type=int,
            default=1,
            help='Number of active tokens to keep per user (default: 1)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        keep_per_user = options['keep_per_user']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        self.stdout.write('Analyzing FCM tokens...')
        
        # Get all users with FCM tokens
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users_with_tokens = User.objects.filter(
            fcmtoken__is_active=True
        ).distinct()
        
        total_deactivated = 0
        total_deleted = 0
        
        for user in users_with_tokens:
            # Get all active tokens for this user, ordered by creation date (newest first)
            active_tokens = FCMToken.objects.filter(
                user=user,
                is_active=True
            ).order_by('-created_at')
            
            active_count = active_tokens.count()
            
            if active_count > keep_per_user:
                # Get IDs of tokens to keep (newest ones)
                tokens_to_keep_ids = list(active_tokens[:keep_per_user].values_list('id', flat=True))
                
                # Get tokens to deactivate (all active tokens except the ones to keep)
                tokens_to_deactivate = FCMToken.objects.filter(
                    user=user,
                    is_active=True
                ).exclude(id__in=tokens_to_keep_ids)
                
                deactivate_count = tokens_to_deactivate.count()
                
                self.stdout.write(f'User {user.username}:')
                self.stdout.write(f'  - Active tokens: {active_count}')
                self.stdout.write(f'  - Keeping: {keep_per_user}')
                self.stdout.write(f'  - Deactivating: {deactivate_count}')
                
                for token in tokens_to_deactivate:
                    self.stdout.write(f'    - Deactivating token ID {token.id} (device: {token.device_id})')
                
                if not dry_run:
                    deactivated = tokens_to_deactivate.update(is_active=False)
                    total_deactivated += deactivated
            
            # Also clean up very old inactive tokens (older than 30 days)
            from datetime import datetime, timedelta
            old_inactive_tokens = FCMToken.objects.filter(
                user=user,
                is_active=False,
                updated_at__lt=datetime.now() - timedelta(days=30)
            )
            
            old_count = old_inactive_tokens.count()
            if old_count > 0:
                self.stdout.write(f'  - Old inactive tokens to delete: {old_count}')
                if not dry_run:
                    deleted = old_inactive_tokens.delete()[0]
                    total_deleted += deleted
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN COMPLETE')
            )
            self.stdout.write(f'Would deactivate: {total_deactivated} tokens')
            self.stdout.write(f'Would delete: {total_deleted} old inactive tokens')
            self.stdout.write('\nRun without --dry-run to apply changes')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'CLEANUP COMPLETE')
            )
            self.stdout.write(f'Deactivated: {total_deactivated} duplicate tokens')
            self.stdout.write(f'Deleted: {total_deleted} old inactive tokens')
            
        # Show final status
        self.stdout.write('\nFinal token status:')
        active_tokens = FCMToken.objects.filter(is_active=True)
        inactive_tokens = FCMToken.objects.filter(is_active=False)
        
        self.stdout.write(f'Active tokens: {active_tokens.count()}')
        self.stdout.write(f'Inactive tokens: {inactive_tokens.count()}')
        
        # Show per-user breakdown
        for user in users_with_tokens:
            user_active = FCMToken.objects.filter(user=user, is_active=True).count()
            if user_active > 0:
                self.stdout.write(f'  - {user.username}: {user_active} active tokens')