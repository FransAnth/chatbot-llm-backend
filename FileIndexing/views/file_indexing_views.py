from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(["POST", "GET"])
def file_indexing(request):

    match (request.method):
        case "GET":
            return JsonResponse({"message": "HI THERE IM WORKING"})
        case "POST":
            return JsonResponse({"message": "Test"})
