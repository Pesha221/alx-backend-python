from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer


# -----------------------------
# Conversation ViewSet
# -----------------------------
class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, and retrieving conversations.
    """
    queryset = Conversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['participants']

    def get_queryset(self):
        """Return conversations where the current user is a participant."""
        user = self.request.user
        return self.queryset.filter(participants=user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to an existing conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            conversation.save()
            return Response({'status': 'participant added'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# -----------------------------
# Message ViewSet
# -----------------------------
class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and sending messages in conversations.
    """
    queryset = Message.objects.all().select_related('sender', 'conversation')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation']

    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            return self.queryset.filter(conversation__conversation_id=conversation_id)
        return self.queryset.none()

    def perform_create(self, serializer):
        """Set the sender automatically to the current user."""
        serializer.save(sender=self.request.user)

