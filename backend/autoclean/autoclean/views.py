from django.http import HttpResponse, JsonResponse

from api.tasks import test_task
from api.models import TaskProgress

def test_view(request):
    return HttpResponse("test")

def test_task_view(request):
    task_progress = TaskProgress(
        uuid=TaskProgress.makeUUID(),
        status=TaskProgress.Status.PENDING.value,
        message="Task created in queue. Pending for processing...",
        error=None,
        percentage=0.0,
        user=None
    )
    
    task_progress.save()
    
    test_task.delay({
        "task_progress_id": task_progress.id
    })

    return JsonResponse({
        "task_progress_uuid": task_progress.uuid
    })