import os
from pathlib import Path
import sys

# Put project root on path (helps when running uvicorn from workspace)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure Django before importing app modules that rely on it
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'one2one_chat.settings')
import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from messaging.jwt_auth import JWTAuthMiddleware
import messaging.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(messaging.routing.websocket_urlpatterns)
        )
    ),
})