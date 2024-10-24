from django.core.management.base import BaseCommand

from autoclean.seeders.users import UserSeeder

class Command(BaseCommand):
    help = 'Seed the database with fake users'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(f'Seeding Database...'))

        user_seeder = UserSeeder()
        user_seeder.createsuperuser()
        user_seeder.seed(10)

        self.stdout.write(self.style.SUCCESS(f'Database seeded successfully.'))