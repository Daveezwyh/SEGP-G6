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
    ImportScanResultSerializer, ImportScanResultActionSerializer,
    TaskProgressSerializer
)
from .tasks import read_file_to_import_data, copy_import_data_original, scan_import, clean_import
from .models import TaskProgress, Import, ImportData, ImportScanResult, ImportScanResultAction
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
    queryset = Import.objects.all()
    serializer_class = ImportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AutocleanAPIPagination

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
    
    @extend_schema(
        methods=["POST"],
        description="Starts the cleaning process for the specified import instance.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Cleaning process started successfully",
                examples=[
                    OpenApiExample(
                        name="Successful Response",
                        description="Returns a UUID indicating the cleaning task has started.",
                        value={"task_progress_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Invalid request data",
                examples=[
                    OpenApiExample(
                        name="Missing id",
                        description="Occurs when the 'id' field is not provided in the request body.",
                        value={"error": "id is required."},
                        response_only=True
                    )
                ]
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Import not found",
                examples=[
                    OpenApiExample(
                        name="Import Not Found",
                        description="Occurs when the specified 'id' does not exist in the database.",
                        value={"error": "Import instance not found."},
                        response_only=True
                    )
                ]
            ),
        },
        examples=[
            OpenApiExample(
                name="Valid Request",
                description="A valid request with an existing import ID.",
                value={"id": 5},
                request_only=True
            )
        ],
    )
    @action(detail=False, methods=["post"], url_path="start-clean")
    def start_clean(self, request):
        data = request.data

        import_id = data.get("id")
        if not import_id:
            return Response({"error": "id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            import_instance = Import.objects.get(id=import_id)
        except Import.DoesNotExist:
            return Response({"error": "Import instance not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if import_instance.status != Import.Status.NEW:
            return Response({"error": "Import has already been processed."}, status=status.HTTP_400_BAD_REQUEST)

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
            clean_import.s({
                "task_progress_id": task_progress.id,
                "import_id": import_instance.id
            })
        )

        task_chain.apply_async()

        import_instance.status = Import.Status.PROCESSING.value
        import_instance.save()

        serializer = ImportSerializer(import_instance)
        response_data = serializer.data
        response_data.update({
            "task_progress_uuid": task_progress.uuid
        })

        return Response(response_data, status=status.HTTP_201_CREATED)

class ImportScanResultActionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ImportScanResultActionSerializer,
        responses={
            200: ImportScanResultActionSerializer,
        },
        description="Update a single Import Scan Result Action object.",
        examples=[
            OpenApiExample(
                "Valid PATCH Request",
                value={"id": 1, "import_scan_result_id": 5, "activate": False},
                request_only=True
            ),
            OpenApiExample(
                "Successful Response",
                value={
                    "id": 1,
                    "title": "Fix Issue",
                    "description": "This action fixes the issue",
                    "cleaner": "SomeCleaner",
                    "cleaner_id": 3,
                    "activate": False,
                    "import_scan_result_id": 5
                },
                response_only=True
            )
        ]
    )
    def patch(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, dict) or "id" not in data or "import_scan_result_id" not in data or "activate" not in data:
            return Response({"error": "Invalid input data."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = get_object_or_404(
                ImportScanResultAction, 
                id=data["id"], 
                import_scan_result_id=data["import_scan_result_id"]
            )

            # Update only the 'activate' field
            update_serializer = ImportScanResultActionSerializer(instance, data={"activate": data["activate"]}, partial=True)

            if update_serializer.is_valid():
                update_serializer.save()

                response_serializer = ImportScanResultActionSerializer(instance)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            return Response(update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ImportScanResultActionBulkUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ImportScanResultActionSerializer(many=True),
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Successful bulk update of scan result actions.",
                examples=[
                    OpenApiExample(
                        "Successful Response (200 OK)",
                        value={
                            "message": "Updated successfully",
                            "updated": [
                                {
                                    "id": 1,
                                    "title": "Fix Issue",
                                    "description": "This action fixes the issue",
                                    "cleaner": "SomeCleaner",
                                    "cleaner_id": 3,
                                    "activate": True,
                                    "import_scan_result_id": 5
                                },
                                {
                                    "id": 2,
                                    "title": "Resolve Conflict",
                                    "description": "Resolves data conflict",
                                    "cleaner": "SomeCleaner",
                                    "cleaner_id": 7,
                                    "activate": False,
                                    "import_scan_result_id": 5
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
                                    "title": "Resolve Conflict",
                                    "description": "Resolves data conflict",
                                    "cleaner": "SomeCleaner",
                                    "cleaner_id": 7,
                                    "activate": False,
                                    "import_scan_result_id": 5
                                }
                            ],
                            "errors": [{"id": 3, "error": "Not found."}]
                        },
                        response_only=True
                    )
                ]
            ),
        },
        description="Bulk update a list of Import Scan Result Actions.",
        examples=[
            OpenApiExample(
                "Valid PATCH Request",
                value={"id": 1, "import_scan_result_id": 5, "activate": False},
                request_only=True
            )
        ]
    )
    def patch(self, request, *args, **kwargs):
        data_list = request.data

        if not isinstance(data_list, list):
            return Response({"error": "Expected a list of objects."}, status=status.HTTP_400_BAD_REQUEST)

        updated_results = []
        errors = []

        for data in data_list:
            if "id" not in data or "import_scan_result_id" not in data or "activate" not in data:
                errors.append({"error": f"Missing 'id', 'import_scan_result_id', or 'activate' in {data}"})
                continue

            try:
                instance = get_object_or_404(
                    ImportScanResultAction, 
                    id=data["id"], 
                    import_scan_result_id=data["import_scan_result_id"]
                )

                # Update only the 'activate' field
                update_serializer = ImportScanResultActionSerializer(instance, data={"activate": data["activate"]}, partial=True)

                if update_serializer.is_valid():
                    update_serializer.save()
                    updated_results.append(update_serializer.data)
                else:
                    errors.append({"id": data["id"], "error": update_serializer.errors})

            except Exception as e:
                errors.append({"id": data["id"], "error": str(e)})

        if errors:
            return Response({"updated": updated_results, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

        return Response({"message": "Updated successfully", "updated": updated_results}, status=status.HTTP_200_OK)