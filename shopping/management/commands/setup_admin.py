from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Create super user for application'

    def handle(self, *args, **options):

        User = get_user_model()

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Successfully created superuser'))

        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))
