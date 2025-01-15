from django.shortcuts import render,get_object_or_404, redirect
from django.http import JsonResponse
from .services import store_single_prediction, store_bulk_predictions

# View for single comment prediction
def predict_toxicity_single(request, comment_id):
    """
    View to predict toxicity for a single comment and store the result in the database.
    """
    success = store_single_prediction(comment_id)
    if success:
        return JsonResponse({"message": "Prediction stored successfully for the comment."}, status=200)
    else:
        return JsonResponse({"message": "Comment not found or an error occurred."}, status=400)

# View for bulk comment prediction
def predict_toxicity_bulk(request):
    """
    View to predict toxicity for multiple comments and store the results in the database.
    """
    if request.method == "POST":
        comment_ids = request.POST.getlist('comment_ids[]', [])
        success = store_bulk_predictions(comment_ids)
        if success:
            return JsonResponse({"message": "Predictions stored successfully for selected comments."}, status=200)
        else:
            return JsonResponse({"message": "An error occurred while storing predictions."}, status=400)
    return JsonResponse({"message": "Invalid request method."}, status=405)
