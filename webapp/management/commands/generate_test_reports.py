# webapp/management/commands/generate_test_reports.py
from django.core.management.base import BaseCommand
from webapp.models import ReportHistory, Session, User
import datetime

class Command(BaseCommand):
    help = 'Generate 5 test report history entries'

    def handle(self, *args, **kwargs):
        # Get or create a test user
        user, created = User.objects.get_or_create(username='test_user', defaults={'password': 'test123'})
        
        # Create 5 sessions (each session can have one report history)
        for i in range(5):
            session = Session.objects.create(
                user=user,
                dp_model_type='TestModel',
                dp_model_parameters={'param': i},
                mitigators='None',
                epsilon=1.0,
            )
            ReportHistory.objects.create(
                session=session,
                name=f'Test Report {i+1}',
                content=f'This is the content of test report number {i+1}.',
            )
            self.stdout.write(self.style.SUCCESS(f"Created Test Report {i+1}"))
