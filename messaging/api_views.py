from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, MessageSerializer
from .models import Message
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'detail': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(password)
        except Exception:
            # skip validators in minimal example
            pass
        user = User.objects.create_user(username=username, password=password)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TokenObtainPairViewSimple(TokenObtainPairView):
    permission_classes = (AllowAny,)


class UserListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


class MessageListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        other_id = self.request.query_params.get('other_id')
        if not other_id:
            return Message.objects.none()
        return Message.objects.filter(
            Q(sender=self.request.user, recipient_id=other_id) | Q(sender_id=other_id, recipient=self.request.user)
        ).order_by('timestamp')

    def perform_create(self, serializer):
        # allow recipient to be provided either in body or as query param `other_id`
        recipient_id = self.request.data.get('recipient_id') or self.request.query_params.get('other_id')
        content = self.request.data.get('content')
        errors = {}
        if not recipient_id:
            errors['recipient_id'] = 'This field is required.'
        if not content:
            errors['content'] = 'This field is required.'
        if errors:
            raise ValidationError(errors)

        serializer.save(sender=self.request.user, recipient_id=recipient_id, content=content)


class RoomNameAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        other_id = request.data.get('other_id')
        if not other_id:
            return Response({'detail': 'other_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            other = User.objects.get(id=other_id)
        except User.DoesNotExist:
            return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        a, b = sorted([int(request.user.id), int(other.id)])
        room_name = f"{a}_{b}"
        return Response({'room_name': room_name})


class InboxAPIView(generics.ListAPIView):
    """Return the last 5 messages received by the authenticated user."""
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user).order_by('-timestamp')[:5]
