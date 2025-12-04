from urllib.parse import parse_qs
from channels.db import database_sync_to_async
import traceback


class JWTAuthMiddleware:
    """ASGI middleware that authenticates WebSocket connections using a JWT
    access token provided in the query string as `?token=...` or
    `?access_token=...`.

    Implemented as a middleware factory that returns an instance following
    Channels' recommended pattern to avoid AppRegistry issues at import time.
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return JWTAuthMiddlewareInstance(scope, self.inner)


class JWTAuthMiddlewareInstance:
    def __init__(self, scope, inner):
        # copy scope so we can safely modify it
        self.scope = dict(scope)
        self.inner = inner

    async def __call__(self, receive, send):
        try:
            query_string = self.scope.get("query_string", b"").decode()
            params = parse_qs(query_string)
            token = params.get("token", [None])[0] or params.get("access_token", [None])[0]

            if token:
                # Lazy imports to avoid importing Django at module import time
                from rest_framework_simplejwt.tokens import AccessToken
                from django.contrib.auth import get_user_model

                try:
                    access_token = AccessToken(token)
                    user_id = access_token.get("user_id")
                    if user_id:
                        User = get_user_model()
                        user = await database_sync_to_async(User.objects.get)(id=user_id)
                        self.scope["user"] = user
                        print(f"[jwt_auth] Authenticated WS user_id={user_id}")
                except Exception as exc:
                    # Invalid token — do NOT overwrite scope['user']; let session auth run
                    print(f"[jwt_auth] invalid token: {exc}")
                    traceback.print_exc()
        except Exception as exc:
            print(f"[jwt_auth] error parsing token: {exc}")
            traceback.print_exc()

        inner = self.inner(self.scope)
        return await inner(receive, send)
# messaging/jwt_auth.py  ← REPLACE THIS FILE COMPLETELY
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)

        # Accept BOTH: ?token=... and ?access_token=...
        token = params.get("token", [None])[0] or params.get("access_token", [None])[0]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                scope["user"] = user
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)