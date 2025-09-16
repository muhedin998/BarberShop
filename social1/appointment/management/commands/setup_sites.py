from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup Sites for production domains automatically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Define the sites that should exist
        sites_config = [
            {
                'id': 8,
                'domain': 'frizerskisalonhasko.com',
                'name': 'Frizerski salon Hasko - Primary'
            },
            {
                'id': 9,
                'domain': 'evoluci4n.online',
                'name': 'Frizerski salon Hasko - Alternative'
            },
            # Add www versions
            {
                'id': 10,
                'domain': 'www.frizerskisalonhasko.com',
                'name': 'Frizerski salon Hasko - WWW'
            },
            {
                'id': 11,
                'domain': 'www.evoluci4n.online',
                'name': 'Frizerski salon Hasko - WWW Alt'
            }
        ]

        for site_config in sites_config:
            site_id = site_config['id']
            domain = site_config['domain']
            name = site_config['name']
            
            try:
                site = Site.objects.get(id=site_id)
                if site.domain != domain or site.name != name:
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Would update Site ID {site_id}: {site.domain} -> {domain}'
                            )
                        )
                    else:
                        site.domain = domain
                        site.name = name
                        site.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated Site ID {site_id}: {domain}'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Site ID {site_id} already exists correctly: {domain}'
                        )
                    )
            except Site.DoesNotExist:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Would create Site ID {site_id}: {domain}'
                        )
                    )
                else:
                    site = Site.objects.create(
                        id=site_id,
                        domain=domain,
                        name=name
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created Site ID {site_id}: {domain}'
                        )
                    )

        # Show current SITE_ID setting
        current_site_id = getattr(settings, 'SITE_ID', 1)
        try:
            current_site = Site.objects.get(id=current_site_id)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Current SITE_ID ({current_site_id}) points to: {current_site.domain}'
                )
            )
        except Site.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'ERROR: Current SITE_ID ({current_site_id}) does not exist!'
                )
            )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('Site setup completed successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Dry run completed. Use without --dry-run to apply changes.')
            )