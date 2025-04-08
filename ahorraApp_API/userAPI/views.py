# userAPI/views.py
import random
import uuid


from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from finanzasAPI.models import Cash, Account

class GetUserInfo(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            if not request.user.is_superuser and str(request.user.id) != pk:
                return Response(
                    {'error': 'No tienes permisos para ver otros usuarios'},
                    status=status.HTTP_403_FORBIDDEN
                )
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            user = request.user

        return Response({
            'id': user.id,
            'first_name': user.first_name,
            'username': user.username,
            'email': user.email,
            'last_login': user.last_login,
            'is_superuser': user.is_superuser
        }, status=status.HTTP_200_OK)


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        default_cash, created = Cash.objects.get_or_create(
            name="Efectivo",
            defaults={"currency": "MXN"}
        )

        account_number = f"{uuid.uuid4().hex[:12].upper()}"

        while True:
            account_number = ''.join([str(random.randint(0, 9)) for _ in range(18)])

            if not Account.objects.filter(number_account=account_number).exists():
                break

        Account.objects.create(
            number_account=account_number,
            balance=0.00,
            fk_cash=default_cash,
            fk_user=user
        )

        token, _ = Token.objects.get_or_create(user=user)
        return token

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({
            'token': token.key,
            'user_id': token.user.id,
            'is_superuser': token.user.is_superuser,
            'last_login': token.user.last_login.isoformat() if token.user.last_login else None
        }, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'is_superuser': user.is_superuser,
                'user_id': user.id,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateLastLoginView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk=None):
        if pk and str(request.user.id) != pk and not request.user.is_superuser:
            return Response(
                {'error': 'No tienes permisos para actualizar otro usuario'},
                status=status.HTTP_403_FORBIDDEN
            )

        user = request.user if not pk else User.objects.get(pk=pk)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response({
            'last_login': user.last_login.isoformat()
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'detail': 'Sesión cerrada correctamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)