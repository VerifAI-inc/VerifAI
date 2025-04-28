# webapp/views.py
from rest_framework.generics import ListAPIView
from .models import ReportHistory
from .serializers import ReportHistorySerializer
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UploadSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from ml_modules.model_loader import load_model
from django.conf import settings
from django.http import JsonResponse
from .models import Session, AccuracyResult, PrivacyEvaluationResult, FairnessEvaluationResult
from django.core.management import call_command
from .tasks import train_model_task

class ReportHistoryList(ListAPIView):
    queryset = ReportHistory.objects.all().order_by('-creation_date')
    serializer_class = ReportHistorySerializer

class UploadAPIView(APIView):
    def get_permissions(self):
        # Allow unauthenticated access for OPTIONS requests
        if self.request.method == "OPTIONS":
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def post(self, request, format=None):
        print("Received Data:", request.data)  
        serializer = UploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            session = serializer.save()
            
            # 🧠 Trigger background training after upload
            train_model_task.delay(session.id)

            return Response(
                {
                    "message": "Files uploaded and session created successfully. Training started in background.",
                    "session_id": session.id
                },
                status=status.HTTP_201_CREATED
            )
        print("Validation Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PreviewModelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if 'modelFile' not in request.FILES:
            return Response({"error": "No model file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        model_file = request.FILES['modelFile']
        # Save the uploaded file temporarily
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_models")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, model_file.name)
        
        with open(temp_path, "wb+") as destination:
            for chunk in model_file.chunks():
                destination.write(chunk)
        
        # Get epsilon and num_features from request (or use defaults)
        epsilon = float(request.data.get("epsilon", 1.0))
        num_features = int(request.data.get("num_features", 10))
        
        try:
            # Call your load_model function
            model_obj, original_model, dp_model_obj = load_model(temp_path, epsilon, num_features)
            response_data = {
                "model_type": model_obj.__class__.__name__,
                "dp_model_name": dp_model_obj.__class__.__name__,
            }
        except Exception as e:
            response_data = {"error": str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return Response(response_data, status=status.HTTP_200_OK)

def store_results(request):
    session = Session.objects.last()  # You can later adjust to request.user if needed

    epsilons = [0.0, 0.1, 1, 5, 10]  # Always include 0.0 too (for no-DP case)

    all_results = {}

    for epsilon in epsilons:
        # --- Privacy Results ---
        privacy_results = PrivacyEvaluationResult.objects.filter(session=session, epsilon=epsilon)

        privacy_data = {}
        for result in privacy_results:
            key = ""
            if result.mitigator.lower() == "orig" and not result.with_dp:
                key = "orig_without_dp"
            elif result.mitigator.lower() == "orig" and result.with_dp:
                key = "orig_with_dp"
            elif result.mitigator.lower() != "orig" and not result.with_dp:
                key = "mitigator_without_dp"
            elif result.mitigator.lower() != "orig" and result.with_dp:
                key = "mitigator_with_dp"

            privacy_data[key] = {
                "g0-": result.privacy_risk_g0_minus,
                "g0+": result.privacy_risk_g0_plus,
                "g1-": result.privacy_risk_g1_minus,
                "g1+": result.privacy_risk_g1_plus,
            }

        # --- Accuracy Results ---
        accuracy_results = AccuracyResult.objects.filter(session=session, epsilon=epsilon)

        accuracy_data = {}
        for result in accuracy_results:
            key = "with_dp" if result.with_dp else "without_dp"
            accuracy_data[key] = {
                "train": result.total_train_acc,
                "test": result.total_test_acc,
                "subgroups": {
                    "g0-": result.test_acc_g0_minus,
                    "g0+": result.test_acc_g0_plus,
                    "g1-": result.test_acc_g1_minus,
                    "g1+": result.test_acc_g1_plus,
                }
            }

        # --- Fairness Results ---
        fairness_results = FairnessEvaluationResult.objects.filter(session=session, epsilon=epsilon)

        fairness_data = {}
        for result in fairness_results:
            key = ""
            if result.mitigator.lower() == "orig" and not result.with_dp:
                key = "orig_without_dp"
            elif result.mitigator.lower() == "orig" and result.with_dp:
                key = "orig_with_dp"
            elif result.mitigator.lower() != "orig" and not result.with_dp:
                key = "mitigator_without_dp"
            elif result.mitigator.lower() != "orig" and result.with_dp:
                key = "mitigator_with_dp"

            fairness_data[key] = {
                "bal_acc": result.bal_acc,
                "avg_odds_diff": result.avg_odds_diff,
                "disp_imp": result.disp_imp,
                "stat_par_diff": result.stat_par_diff,
                "eq_opp_diff": result.eq_opp_diff,
                "theil_ind": result.theil_ind,
            }

        # --- Collect everything for this epsilon ---
        all_results[str(epsilon)] = {
            "privacy": privacy_data,
            "accuracy": accuracy_data,
            "fairness": fairness_data,
        }

    return JsonResponse(all_results)