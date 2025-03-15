from django.contrib.auth.models import User
from faker import Faker

class UserSeeder:
    def seed(self, count=10):
        print(f'\nSeeding Users...')
        for _ in range(count):
            self.create()
        print(f'Users seeded successfully.\n')
    
    def createsuperuser(self):
        if User.objects.filter(username="root").exists():
            print("\nSuperuser 'root' already exists. Skipping creation.")
            return

        User.objects.create_superuser(
            username="root",
            email="root@email.com",
            password="password"
        )
        print("Superuser 'root' created successfully.")

    def create(self):
        faker = Faker()
        username = faker.user_name()
        email = faker.email()
        password = "password"
        first_name = faker.first_name()
        last_name = faker.last_name()

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )