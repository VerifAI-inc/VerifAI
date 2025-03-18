import os  # Ensure os is imported if used
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UploadSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from ml_modules.model_loader import load_model
from django.conf import settings



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
            return Response(
                {
                    "message": "Files uploaded and session created successfully.",
                    "session_id": session.id
                },
                status=status.HTTP_201_CREATED
            )
        print("Validation Errors:", serializer.errors)  # Print errors in Django logs
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
