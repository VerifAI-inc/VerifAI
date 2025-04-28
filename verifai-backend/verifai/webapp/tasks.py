# webapp/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def train_model_task(session_id):
    """
    Background task to train models and store results.
    """
    try:
        call_command('store_results')
        return "Training and storing completed!"
    except Exception as e:
        return f"Error during training: {str(e)}"
