from django.http import HttpResponse

from api.tasks import add

def test_view(request):
    #add.delay(4, 4)
    return HttpResponse("test")