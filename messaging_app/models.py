import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


# ==========================
# Custom User Model
# ==========================
class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Remove username requirement and use email as username field
    username = None

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)

    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


# ==========================
# Conversation Model
# ==========================
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # A conversation has multiple users
    participants = models.ManyToManyField(User, related_name='conversations')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


# ==========================
# Message Model
# ==========================
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    message_body = models.TextField()

    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.email}"
