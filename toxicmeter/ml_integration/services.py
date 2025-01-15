import requests
from facebook.models import FacebookComment
from .models import ToxicityParameters
# functions = predict_single_comment, predict_bulk_comments, store_single_prediction, store_bulk_predictions
def predict_single_comment(comment_text):
    """
    Sends a single comment to the Flask ML service for toxicity prediction.
    
    Args:
        comment_text (str): The text of the comment to analyze.

    Returns:
        dict: A dictionary containing the predictions (e.g., toxic, threat, etc.) or None if the request fails.
    """
    url = "http://127.0.0.1:5000/predict"
    headers = {"Content-Type": "application/json"}
    payload = {"text": comment_text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during single comment prediction: {e}")
        return None

def predict_bulk_comments(comments):
    """
    Sends multiple comments to the Flask ML service for bulk toxicity prediction.

    Args:
        comments (list): A list of comment strings to analyze.

    Returns:
        list: A list of dictionaries containing comments and their predictions, or None if the request fails.
    """
    url = "http://127.0.0.1:5000/predict_bulk"
    headers = {"Content-Type": "application/json"}
    payload = {"comments": comments}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during bulk comment prediction: {e}")
        return None

def store_single_prediction(comment_id):
    """
    Fetches a single comment, predicts toxicity, and stores it in the database.
    """
    try:
        # Get the comment from the database
        comment = FacebookComment.objects.get(id=comment_id)

        # Get the prediction using Step 1's function
        prediction = predict_single_comment(comment.content)

        if prediction:
            # Store the prediction in ToxicityParameters
            ToxicityParameters.objects.update_or_create(
                comment=comment,
                defaults={
                    'toxic': prediction['toxic'],
                    'severe_toxic': prediction['severe_toxic'],
                    'obscene': prediction['obscene'],
                    'threat': prediction['threat'],
                    'insult': prediction['insult'],
                    'identity_hate': prediction['identity_hate'],
                },
            )
        else:
            print(f"Prediction failed for comment ID: {comment_id}")
            return False
        return True
    except FacebookComment.DoesNotExist:
        return False

def store_bulk_predictions(comment_ids):
    """
    Fetches multiple comments, predicts toxicity, and stores them in the database.
    """
    try:
        # Get the comments from the database
        comments = FacebookComment.objects.filter(id__in=comment_ids)

        # Prepare the content for prediction
        comments_data = [comment.content for comment in comments]

        # Get the bulk predictions using Step 1's function
        bulk_predictions = predict_bulk_comments(comments_data)

        # Store predictions in ToxicityParameters
        for comment, result in zip(comments, bulk_predictions):
            ToxicityParameters.objects.update_or_create(
                comment=comment,
                defaults={
                    'toxic': result['prediction']['toxic'],
                    'severe_toxic': result['prediction']['severe_toxic'],
                    'obscene': result['prediction']['obscene'],
                    'threat': result['prediction']['threat'],
                    'insult': result['prediction']['insult'],
                    'identity_hate': result['prediction']['identity_hate'],
                },
            )
        return True
    except Exception as e:
        return False
