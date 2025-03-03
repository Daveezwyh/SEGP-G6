from django.core.management.base import BaseCommand
from autoclean.seeders.cleaners import CleanerSeeder

class Command(BaseCommand):
    help = "Seed the Cleaner data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Seeding Cleaners..."))

        cleaner_seeder = CleanerSeeder()
        cleaner_seeder.seed()

        self.stdout.write(self.style.SUCCESS("Cleaners seeded successfully."))