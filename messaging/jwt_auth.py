from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class JWTAuthMiddleware:
    """Custom ASGI middleware that authenticates WebSocket connections using
    a JWT access token provided in the query string as `?token=...`.

    If no token is provided or token is invalid, leaves `scope['user']`
    unchanged so that session-based auth (AuthMiddlewareStack) can apply.
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return JWTAuthMiddlewareInstance(scope, self.inner)


class JWTAuthMiddlewareInstance:
    def __init__(self, scope, inner):
        self.scope = dict(scope)
        self.inner = inner

    async def __call__(self, receive, send):
        query = self.scope.get('query_string', b'').decode()
        params = parse_qs(query)
        token_list = params.get('token') or params.get('access_token')
        token = token_list[0] if token_list else None

        if token:
            try:
                access = AccessToken(token)
                user_id = access.get('user_id')
                if user_id:
                    user = await database_sync_to_async(User.objects.get)(id=user_id)
                    self.scope['user'] = user
            except Exception:
                # Invalid token -> leave scope['user'] as Anonymous or unchanged
                self.scope['user'] = AnonymousUser()

        inner = self.inner(self.scope)
        return await inner(receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
