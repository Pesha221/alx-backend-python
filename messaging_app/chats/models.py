#!/usr/bin/env python3
"""Django models for User, Conversation, and Message."""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model extending Django AbstractUser."""
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    # Remove username to use email as unique identifier
    username = None

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No required username field since removed

    def __str__(self):
        return self.email


class Conversation(models.Model):
    """Conversation tracking which users are involved."""
    conversation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """A message sent by a user within a conversation."""
    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages"
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Added as required

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"
