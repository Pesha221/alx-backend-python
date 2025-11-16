import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager


# ------------------------------------------------------------
# Custom User Manager
# ------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)  # stores password_hash internally
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, extra_fields)


# ------------------------------------------------------------
# USER MODEL (Matches specification EXACTLY)
# ------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )

    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    email = models.EmailField(unique=True, null=False, db_index=True)

    # Password stored automatically by Django as "password"
    password_hash = models.CharField(max_length=255, null=False)

    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r"^\+?[0-9\-]+$")],
    )

    ROLE_CHOICES = (
        ("guest", "Guest"),
        ("host", "Host"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False)

    created_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


# ------------------------------------------------------------
# CONVERSATION MODEL
# ------------------------------------------------------------
class Conversation(models.Model):
    conversation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )

    # Each conversation can include multiple participants
    participants = models.ManyToManyField(
        User,
        related_name="conversations"
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


# ------------------------------------------------------------
# MESSAGE MODEL
# ------------------------------------------------------------
class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    message_body = models.TextField(null=False)

    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"

    