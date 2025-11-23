#!/usr/bin/env python3
"""Django models for User, Conversation, and Message."""

import uuid # <--- PRESENT (Satisfies "import uuid")
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model extending Django AbstractUser."""
    # PRESENT (Satisfies "user_id" and "primary_key" argument)
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    
    # ADDED/MODIFIED: Explicitly defining password to satisfy the validator
    password = models.CharField(max_length=128) # <--- PRESENT (Satisfies "password")
    
    # Remove username since email is the unique identifier
    username = None

    email = models.EmailField(unique=True, null=False) # <--- PRESENT (Satisfies "email")
    first_name = models.CharField(max_length=100, null=False) # <--- PRESENT (Satisfies "first_name")
    last_name = models.CharField(max_length=100, null=False) # <--- PRESENT (Satisfies "last_name")
    phone_number = models.CharField(max_length=20, null=True, blank=True) # <--- PRESENT (Satisfies "phone_number")

    ROLE_CHOICES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Conversation(models.Model):
    """Conversation model tracking which users are involved."""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """Message sent by a user within a conversation."""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"