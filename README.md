# 1v1 Real-time Chat (Django + Channels) - Backend Only

This project provides authentication and a realtime 1-vs-1 chat backend using Django, Channels and DRF.


### Docker Support

You can also run this project using Docker and Docker Compose.

1. **Build and Run**:
   ```bash
   docker-compose up -d --build
   ```
   The application will be available at `http://localhost:8000`.

2. **Stop Containers**:
   ```bash
   docker-compose down
   ```

3. **View Logs**:
   ```bash
   docker-compose logs -f
   ```

### Local Development (without Docker)

1. Create & activate a virtualenv (if not already):
   ```bash
   python -m venv env
   source env/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations and create a user:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
4. Run development server:
   ```bash
   python manage.py runserver
   ```

API endpoints (Postman-ready)

- Register (create user):

  POST /api/register/
  Body (JSON): { "username": "alice", "password": "safe-password" }

- Obtain JWT token:

  POST /api/token/
  Body (JSON): { "username": "alice", "password": "safe-password" }
  Response: { "access": "<token>", "refresh": "<refresh>" }

- Refresh token:

  POST /api/token/refresh/
  Body (JSON): { "refresh": "<refresh>" }

- List users (requires Authorization: Bearer <access>):

  GET /api/users/

- Get messages between authenticated user and other user (query param `other_id`):

  GET /api/messages/?other_id=2

- Send message:

  POST /api/messages/
  Body (JSON): { "recipient_id": 2, "content": "Hello" }

- Create or obtain room name for WebSocket (to connect to `/ws/chat/<room_name>/`):

  POST /api/room/
  Body (JSON): { "other_id": 2 }
  Response: { "room_name": "1_2" }

WebSocket endpoint (for realtime):

- Connect as authenticated user (your browser or a WebSocket client) to:

  ws://127.0.0.1:8000/ws/chat/<room_name>/

Notes:
- Uses in-memory channel layer for development. For production, configure Redis in `CHANNEL_LAYERS`.
- This backend exposes JWT authentication via SimpleJWT. For WebSocket authentication you can either rely on session cookies (AuthMiddlewareStack) or implement a custom JWT Auth middleware for Channels.
