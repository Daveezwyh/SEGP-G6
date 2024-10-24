from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer