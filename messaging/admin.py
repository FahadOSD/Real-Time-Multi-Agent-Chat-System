from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'content', 'timestamp')
    list_filter = ('sender', 'recipient')
    search_fields = ('content', 'sender__username', 'recipient__username')
