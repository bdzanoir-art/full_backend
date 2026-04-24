from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid credentials", "details": "User not found with this email."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_auth = authenticate(username=user.username, password=password)
            
            if user_auth is not None:
                return Response({
                    "message": "Login successful",
                    "user": {
                        "id": user_auth.id,
                        "username": user_auth.username,
                        "email": user_auth.email
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid credentials", "details": "Incorrect password."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
