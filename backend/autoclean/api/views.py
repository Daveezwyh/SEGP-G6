from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from celery import chain
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse

from .serializers import (
    UserSerializer, UploadImportSerializer, ImportSerializer, ImportDataSerializer, ImportScanResultSerializer,
    TaskProgressSerializer
)
from .tasks import read_file_to_import_data, copy_import_data_original, scan_import
from .models import TaskProgress, Import, ImportData, ImportScanResult
from autoclean.utils import AutocleanAPIPagination

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class TaskProgressRetrieveAPIView(generics.RetrieveAPIView):
    queryset = TaskProgress.objects.all()
    serializer_class = TaskProgressSerializer
    lookup_field = 'uuid'

    def get_object(self):
        try:
            return TaskProgress.objects.get(uuid=self.kwargs['uuid'])
        except TaskProgress.DoesNotExist:
            raise NotFound(detail="TaskProgress with this UUID does not exist.")

class ImportUploadView(APIView):
    serializer_class = UploadImportSerializer
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'The file to upload.',
                    },
                    'description': {
                        'type': 'string',
                        'description': 'Optional description for the import.',
                    },
                },
                'required': ['file'],
            }
        },
        responses={
            201: OpenApiResponse(response=UploadImportSerializer, description="File uploaded successfully."),
            400: OpenApiResponse(description="Bad request. Invalid input."),
        },
        summary="Upload Import File",
        description="Endpoint to upload a file for import processing. The file must be a valid CSV or Excel file.",
    )
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
                copy_import_data_original.s(),
                scan_import.s()
            )

            task_chain.apply_async()

            response_data = serializer.data.copy()
            response_data.update({
                "task_progress_uuid": task_progress.uuid
            })

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        paginator = AutocleanAPIPagination()
        page = paginator.paginate_queryset(import_data, request)
        if page is not None:
            serializer = ImportDataSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ImportDataSerializer(import_data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='scan-results')
    def scan_results(self, request, pk=None):
        import_instance = self.get_object()
        import_scan_results = ImportScanResult.objects.filter(import_model=import_instance)

        serializer = ImportScanResultSerializer(import_scan_results, many=True)
        return Response(serializer.data)