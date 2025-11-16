from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password

# -----------------------------
# 1. User Serializer
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    # Explicit CharFields
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)  # Do not expose password
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'password', 'date_joined']

    def create(self, validated_data):
        # Hash password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Hash password if it's being updated
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)

# -----------------------------
# 2. Message Serializer
# -----------------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']

# -----------------------------
# 3. Conversation Serializer
# -----------------------------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()  # Nested messages
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']

    def get_messages(self, obj):
        # Return serialized messages for this conversation
        messages = obj.messages.order_by('sent_at')
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        # Example validation
        request = self.context.get('request')
        if request and not request.user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated to access conversation.")
        return data
