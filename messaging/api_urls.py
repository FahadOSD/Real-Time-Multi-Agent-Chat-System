from django.urls import path
from . import api_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', api_views.RegisterAPIView.as_view(), name='api-register'),
    path('token/', api_views.TokenObtainPairViewSimple.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', api_views.UserListAPIView.as_view(), name='api-users'),
    path('messages/', api_views.MessageListCreateAPIView.as_view(), name='api-messages'),
    path('room/', api_views.RoomNameAPIView.as_view(), name='api-room'),
    path('inbox/', api_views.InboxAPIView.as_view(), name='api-inbox'),
]
