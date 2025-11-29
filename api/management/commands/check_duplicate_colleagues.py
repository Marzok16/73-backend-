from django.core.management.base import BaseCommand
from django.db.models import Count
from api.models import Colleague


class Command(BaseCommand):
    help = 'Check for duplicate colleague names in the database'

    def handle(self, *args, **options):
        """
        Check for colleagues with duplicate names (case-insensitive).
        This is a read-only check that does not modify any data.
        """
        self.stdout.write(self.style.SUCCESS('Checking for duplicate colleague names...'))
        
        # Find duplicate names (case-insensitive)
        from django.db.models.functions import Lower
        
        duplicates = (
            Colleague.objects
            .values(lower_name=Lower('name'))
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS(
                '✓ No duplicate colleague names found. All names are unique.'
            ))
            return
        
        self.stdout.write(self.style.WARNING(
            f'\n⚠ Found {len(duplicates)} duplicate name(s):\n'
        ))
        
        total_duplicates = 0
        for dup in duplicates:
            name_lower = dup['lower_name']
            count = dup['count']
            total_duplicates += count - 1
            
            # Get all colleagues with this name
            colleagues = Colleague.objects.filter(name__iexact=name_lower)
            
            self.stdout.write(self.style.WARNING(f'\nName: "{name_lower}" ({count} instances)'))
            for colleague in colleagues:
                self.stdout.write(
                    f'  - ID: {colleague.id}, Name: "{colleague.name}", '
                    f'Status: {colleague.status}, Created: {colleague.created_at}'
                )
        
        self.stdout.write(self.style.WARNING(
            f'\n⚠ Total duplicate entries: {total_duplicates}'
        ))
        self.stdout.write(self.style.NOTICE(
            '\nRecommendation: Review these duplicates and decide whether to:'
        ))
        self.stdout.write('  1. Merge the duplicate entries')
        self.stdout.write('  2. Rename one to make it unique (e.g., add year or identifier)')
        self.stdout.write('  3. Delete the unwanted duplicate(s)')
