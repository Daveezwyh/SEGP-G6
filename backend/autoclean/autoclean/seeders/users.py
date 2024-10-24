from django.contrib.auth.models import User
from faker import Faker

class UserSeeder:
    def seed(self, count=10):
        print(f'\nSeeding Users...')
        for _ in range(count):
            self.create()
        print(f'Users seeded successfully.\n')
    
    def createsuperuser(self):
        superuser = User.objects.create_user(
            username='root',
            email='root@email.com',
            password='password',
            is_staff=True,
            is_superuser=True
        )

    def create(self):
        faker = Faker()
        username = faker.user_name()
        email = faker.email()
        password = 'password'
        first_name = faker.first_name()
        last_name = faker.last_name()

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )