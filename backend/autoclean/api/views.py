from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST

from .serializers import UserSerializer
from .serializers import ImportSerializer
from .tasks import read_file_to_import_data

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ImportUploadView(APIView):
    serializer_class = ImportSerializer
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            Import = serializer.save(uploaded_by=request.user)

            uploaded_file = serializer.validated_data['file']
            Import.data = {
                "filename": uploaded_file.name
            }
            Import.save()

            read_file_to_import_data.delay(Import.id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)