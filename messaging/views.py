from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'messaging/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('user_list')
    else:
        form = AuthenticationForm()
    return render(request, 'messaging/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'messaging/user_list.html', {'users': users})


def _room_name_for(user1_id, user2_id):
    a, b = sorted([int(user1_id), int(user2_id)])
    return f"{a}_{b}"


@login_required
def chat_view(request, user_id):
    other = get_object_or_404(User, id=user_id)
    room_name = _room_name_for(request.user.id, other.id)
    # load last 50 messages between two users
    messages = Message.objects.filter(
        (Q(sender=request.user, recipient=other) | Q(sender=other, recipient=request.user))
    ).order_by('timestamp')[:50]

    return render(request, 'messaging/chat.html', {
        'other': other,
        'room_name': room_name,
        'messages': messages,
    })
