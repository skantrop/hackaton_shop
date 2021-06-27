from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, ActivationSerializer, LoginSerializer


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Your account successfully registered', status=status.HTTP_201_CREATED)


class ActivationView(APIView):
    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.activate()
            return Response('Your account is successfully activated', status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    pass


class RestorePasswordView(APIView):
    pass


class ChangePasswordView(APIView):
    pass


class UserProfileView(APIView):
    pass



#TODO: Registration
#TODO: Activation
#TODO: Login
#TODO: Password restore
#TODO: Password reset
#TODO: User Profile
