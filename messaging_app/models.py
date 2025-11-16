import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Used to reference the custom User model


# ==============================================================================
# 1. User Model (Extension of AbstractUser)
# ==============================================================================

class User(AbstractUser):
    """
    Custom User model extending AbstractUser to include UUID primary key,
    phone number, and a user role (guest, host, admin).

    Note: The built-in AbstractUser already provides fields like email, 
    first_name, last_name, and handles password hashing.
    """
    
    # Role choices as defined in the specification
    ROLE_GUEST = 'guest'
    ROLE_HOST = 'host'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = (
        (ROLE_GUEST, 'Guest'),
        (ROLE_HOST, 'Host'),
        (ROLE_ADMIN, 'Admin'),
    )

    # user_id (Primary Key, UUID, Indexed) - Overriding the default PK
    user_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('User ID')
    )

    # email is automatically set to be unique by AbstractUser if used as USERNAME_FIELD,
    # but we ensure it's unique and can be used as the identifier.
    email = models.EmailField(_('email address'), unique=True)
    
    # phone_number (VARCHAR, NULL)
    phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name=_('Phone Number')
    )

    # role (ENUM: 'guest', 'host', 'admin', NOT NULL)
    role = models.CharField(
        max_length=5,
        choices=ROLE_CHOICES,
        default=ROLE_GUEST,
        verbose_name=_('Role')
    )

    # created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP) - handled by AbstractUser's date_joined

    # Fields required for Django custom user model if not using AbstractUser's defaults
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name'] # Keep 'username' for admin compatibility, but it's often dropped in real apps.

    class Meta:
        # Assuming you would set AUTH_USER_MODEL = 'chats.User' in settings.py
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return self.email

# ==============================================================================
# 2. Conversation Model
# ==============================================================================

class Conversation(models.Model):
    """
    Model to track which users are involved in a conversation.
    """
    # conversation_id (Primary Key, UUID, Indexed)
    conversation_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('Conversation ID')
    )
    
    # participants_id (Foreign Key, references User(user_id)) -> ManyToMany relationship
    # A conversation has multiple participants, and a user can be in many conversations.
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        verbose_name=_('Participants')
    )

    # created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')
        ordering = ['-created_at']

    def __str__(self):
        # A simple representation showing the conversation ID
        return f"Conversation {self.conversation_id}"

# ==============================================================================
# 3. Message Model
# ==============================================================================

class Message(models.Model):
    """
    Model for individual messages within a conversation.
    """
    # message_id (Primary Key, UUID, Indexed)
    message_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name=_('Message ID')
    )

    # sender_id (Foreign Key, references User(user_id))
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Sender')
    )
    
    # conversation (Foreign Key to Conversation)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Conversation')
    )

    # message_body (TEXT, NOT NULL)
    message_body = models.TextField(
        verbose_name=_('Message Body')
    )

    # sent_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    sent_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Sent At')
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['sent_at']
        # Adding an index on conversation and sent_at for faster lookup of messages
        # within a specific chat, ordered by time.
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
        ]

    def __str__(self):
        # A simple representation showing the message sender and the first 50 chars
        return f"Message from {self.sender.email} ({self.sent_at.strftime('%Y-%m-%d %H:%M')})"
    