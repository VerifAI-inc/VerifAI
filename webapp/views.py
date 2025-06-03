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
from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes


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

@api_view(["GET"])
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

# read api key from txt file located in ../venv/key.txt
api_key_path = os.path.join(os.path.dirname(__file__), "../myenv/key.txt")
if os.path.exists(api_key_path):
    with open(api_key_path, "r") as f:
        api_key = f.read().strip()
client = OpenAI(api_key=api_key)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def generate_report(request):
    print("🛠️ 1. Received request at /api/generate-report/")

    # Extract the prompt from the request data
    prompt = request.data.get("prompt")
    print("🛠️ 2. Received Prompt:", prompt[:500], "..." if len(prompt) > 500 else "")  # Print first 500 chars

    if not prompt:
        print("🛠️ 2.1: No prompt provided!")
        return Response({"error": "No prompt provided."}, status=400)

    try:
        print("🛠️ 3. Sending prompt to OpenAI API...")

        # OpenAI's new API for conversation-based models
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change the model here as needed
            messages=[
                # {"role": "system", "content": "You are an expert AI evaluation assistant."},
                {"role": "user", "content": "You are an expert AI evaluation assistant." + prompt}
            ],
            # max_tokens=2000,  # Adjust max tokens as necessary
            # temperature=0.7,  # Set the creativity level (0.0-1.0)
        )

        print("🛠️ 4. Received OpenAI response.")

        # Access the response correctly using dot notation
        generated_text = response.choices[0].message  # Correct way to access the message

        print("🛠️ 5. Extracted generated text.")

        # Return the generated text
        return Response({"report_text": generated_text}, status=200)

    except Exception as e:
        print("🛠️ 6. ERROR calling OpenAI:", str(e))
        return Response({"error": str(e)}, status=500)