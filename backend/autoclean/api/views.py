from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from celery import chain
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample

from .serializers import (
    UserSerializer, UploadImportSerializer, ImportSerializer, ImportDataSerializer,
    ImportScanResultSerializer, ImportScanResultUpdateSerializer,
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
    # permission_classes = [IsAuthenticated]
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
    
    @extend_schema(
        responses={200: ImportScanResultSerializer(many=True)},
    )
    @action(detail=True, methods=['get'], url_path='scan-results')
    def scan_results(self, request, pk=None):
        import_instance = self.get_object()
        import_scan_results = ImportScanResult.objects.filter(import_model=import_instance)

        serializer = ImportScanResultSerializer(import_scan_results, many=True)
        return Response(serializer.data)

class ImportScanResultUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ImportScanResultUpdateSerializer,
        responses={
            200: ImportScanResultSerializer,
        },
        description="Update a single Scan Result object.",
        examples=[
            OpenApiExample(
                "Valid PATCH Request",
                value={"id": 1, "import_model_id": 5, "activate": False},
                request_only=True
            ),
            OpenApiExample(
                "Successful Response",
                value={
                    "id": 1,
                    "row": 10,
                    "col": 3,
                    "message": "Some scan result message",
                    "cleaner": "SomeCleaner",
                    "activate": False,
                    "import_model": 5
                },
                response_only=True
            )
        ]
    )
    def patch(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, dict) or "id" not in data or "import_model_id" not in data or "activate" not in data:
            return Response({"error": "Invalid input data."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = get_object_or_404(ImportScanResult, id=data["id"], import_model_id=data["import_model_id"])
            
            update_serializer = ImportScanResultUpdateSerializer(instance, data={"activate": data["activate"]}, partial=True)

            if update_serializer.is_valid():
                update_serializer.save()

                response_serializer = ImportScanResultSerializer(instance)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            return Response(update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ImportScanResultBulkUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ImportScanResultUpdateSerializer(many=True),
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Successful bulk update of scan results.",
                examples=[
                    OpenApiExample(
                        "Successful Response (200 OK)",
                        value={
                            "message": "Updated successfully",
                            "updated": [
                                {
                                    "id": 1,
                                    "row": 10,
                                    "col": 3,
                                    "message": "Some scan result message",
                                    "cleaner": "SomeCleaner",
                                    "activate": True,
                                    "import_model": 5
                                },
                                {
                                    "id": 2,
                                    "row": 12,
                                    "col": 4,
                                    "message": "Another scan result message",
                                    "cleaner": "SomeCleaner",
                                    "activate": False,
                                    "import_model": 5
                                }
                            ]
                        },
                        response_only=True
                    )
                ]
            ),
            207: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Partial success - some records failed.",
                examples=[
                    OpenApiExample(
                        "Partial Success (207 Multi-Status)",
                        value={
                            "updated": [
                                {
                                    "id": 2,
                                    "row": 12,
                                    "col": 4,
                                    "message": "Another scan result message",
                                    "cleaner": "SomeCleaner",
                                    "activate": False,
                                    "import_model": 5
                                }
                            ],
                            "errors": [{"id": 3, "error": "Not found."}]
                        },
                        response_only=True
                    )
                ]
            ),
        },
        description="Update a list of Scan Result objects.",
    )
    def patch(self, request, *args, **kwargs):
        data_list = request.data

        if not isinstance(data_list, list):
            return Response({"error": "Expected a list of objects."}, status=status.HTTP_400_BAD_REQUEST)

        updated_results = []
        errors = []

        for data in data_list:
            if "id" not in data or "import_model_id" not in data or "activate" not in data:
                errors.append({"error": f"Missing 'id', 'import_model_id', or 'activate' in {data}"})
                continue

            try:
                instance = get_object_or_404(ImportScanResult, id=data["id"], import_model_id=data["import_model_id"])

                update_serializer = ImportScanResultUpdateSerializer(instance, data={"activate": data["activate"]}, partial=True)

                if update_serializer.is_valid():
                    update_serializer.save()

                    response_serializer = ImportScanResultSerializer(instance)
                    updated_results.append(response_serializer.data)
                else:
                    errors.append({"id": data["id"], "error": update_serializer.errors})

            except Exception as e:
                errors.append({"id": data["id"], "error": str(e)})

        if errors:
            return Response({"updated": updated_results, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

        return Response({"message": "Updated successfully", "updated": updated_results}, status=status.HTTP_200_OK)