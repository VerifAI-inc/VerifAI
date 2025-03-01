from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import SignupSerializer
from .serializers import LoginSerializer

# Temporary user storage (dictionary)
TEMP_USERS = {}

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            if username in TEMP_USERS:
                return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Store user credentials in a dictionary temporarily
            TEMP_USERS[username] = password
            
            # Simulate a login session
            request.session['username'] = username
            
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Check credentials in temporary storage
            if username in TEMP_USERS and TEMP_USERS[username] == password:
                request.session['username'] = username  # Start a session
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)