import os  # Ensure os is imported if used
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UploadSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

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

