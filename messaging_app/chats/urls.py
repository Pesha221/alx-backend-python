from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
"routers.DefaultRouter()"
# Base router
router = routers.DefaultRouter() # type: ignore
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under a specific conversation
conversation_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation') # type: ignore
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]