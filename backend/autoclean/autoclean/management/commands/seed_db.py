from django.core.management.base import BaseCommand
from django.core.management import call_command

from autoclean.seeders.users import UserSeeder

class Command(BaseCommand):
    help = 'Seed the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(f'Seeding Database...'))

        user_seeder = UserSeeder()
        user_seeder.createsuperuser()
        user_seeder.seed(10)

        call_command("seed_cleaner")

        self.stdout.write(self.style.SUCCESS(f'Database seeded successfully.'))