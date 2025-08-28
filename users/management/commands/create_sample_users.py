from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample users with different roles for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-samples',
            action='store_true',
            help='Create sample users for testing',
        )

    def handle(self, *args, **options):
        if options['create_samples']:
            self.create_sample_users()
        else:
            self.stdout.write(
                self.style.WARNING('Use --create-samples to create sample users')
            )

    def create_sample_users(self):
        """Create sample users for testing"""
        
        # Create admin user
        if not User.objects.filter(username='admin_user').exists():
            admin_user = User.objects.create_user(
                username='admin_user',
                email='admin@smartrecruit.com',
                password='admin123456',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_user.username}')
            )

        # Create recruiter user
        if not User.objects.filter(username='recruteur_user').exists():
            recruiter_user = User.objects.create_user(
                username='recruteur_user',
                email='recruteur@smartrecruit.com',
                password='recruteur123456',
                first_name='Recruteur',
                last_name='User',
                role='recruteur'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created recruiter user: {recruiter_user.username}')
            )

        # Create candidate user
        if not User.objects.filter(username='candidat_user').exists():
            candidate_user = User.objects.create_user(
                username='candidat_user',
                email='candidat@smartrecruit.com',
                password='candidat123456',
                first_name='Candidat',
                last_name='User',
                role='candidat'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created candidate user: {candidate_user.username}')
            )

        self.stdout.write(
            self.style.SUCCESS('Sample users created successfully!')
        )
