from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from api.views import (
    UserViewSet, ImportViewSet, ImportScanResultUpdateView, ImportScanResultBulkUpdateView,
    ImportUploadView,
    TaskProgressRetrieveAPIView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"imports", ImportViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('doc/schema', SpectacularAPIView.as_view(), name='schema'),
    path('doc', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('task-progress/<uuid:uuid>', TaskProgressRetrieveAPIView.as_view(), name='task_progress'),
    path("upload/import", ImportUploadView.as_view(), name='import-upload'),
    path("import-scanresults/update/", ImportScanResultUpdateView.as_view(), name="importscanresult-update"),
    path("import-scanresults/bulk-update/", ImportScanResultBulkUpdateView.as_view(), name="importscanresult-bulk-update"),
]