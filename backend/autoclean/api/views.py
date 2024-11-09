from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from celery import chain
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .serializers import UserSerializer, UploadImportSerializer, ImportSerializer, ImportDataSerializer
from .tasks import read_file_to_import_data, scan_import
from .models import TaskProgress, Import, ImportData

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ImportUploadView(APIView):
    serializer_class = UploadImportSerializer
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

            task_progress = TaskProgress(
                uuid=TaskProgress.makeUUID(),
                status=TaskProgress.Status.PENDING.value,
                message="Task created in queue. Pending for processing...",
                error=None,
                percentage=0.0,
                user=request.user
            )

            task_progress.save()

            task_chain = chain(
                read_file_to_import_data.s({
                    "task_progress_id": task_progress.id,
                    "import_id": Import.id
                }),
                scan_import.s()
            )

            task_chain.apply_async()

            response_data = serializer.data.copy()
            response_data.update({
                "task_progress_uuid": task_progress.uuid
            })

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImportDataPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ImportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Import.objects
    serializer_class = ImportSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="page", type=int, location=OpenApiParameter.QUERY, description="Page number"),
            OpenApiParameter(name="page_size", type=int, location=OpenApiParameter.QUERY, description="Number of results per page"),
        ],
        responses={200: ImportDataSerializer(many=True)},
    )
    @action(detail=True, methods=['get'], url_path='data')
    def import_data(self, request, pk=None):
        import_instance = self.get_object()
        import_data = ImportData.objects.filter(import_model=import_instance).order_by('id')

        paginator = ImportDataPagination()
        page = paginator.paginate_queryset(import_data, request)
        if page is not None:
            serializer = ImportDataSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ImportDataSerializer(import_data, many=True)
        return Response(serializer.data)