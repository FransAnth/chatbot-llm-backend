from django.http import JsonResponse
from rest_framework.decorators import api_view

from .utils.VectorStore import VectorStore


@api_view(["POST", "GET"])
def upload(request):

    match (request.method):
        case "GET":
            return JsonResponse(
                {"message": "This should return the list of uploaded files"}
            )
        case "POST":
            if request.FILES["file"]:
                uploaded_file = request.FILES["file"]

                # Save the file to a specific location
                local_storage_path = "storage/files/"
                with open(
                    local_storage_path + uploaded_file.name, "wb+"
                ) as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Create the embeddings
                vector_db = VectorStore()
                embedding_successful = vector_db.create_embeddings_from_local(
                    local_storage_path + uploaded_file.name
                )

                if not embedding_successful:
                    return JsonResponse(
                        {
                            "message": "Document file type is not supported",
                            "fileName": uploaded_file.name,
                        },
                        status=400,
                    )

                return JsonResponse({"message": "File uploaded successfully"})
            else:
                return JsonResponse(
                    {"error": "No file found in the request"}, status=400
                )
