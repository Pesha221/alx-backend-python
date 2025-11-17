from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter # type: ignore
from .views import ConversationViewSet, MessageViewSet

"routers.DefaultRouter()"

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')

nested_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
nested_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
    
    # Path for REST framework authentication views (api-auth)
    path('api-auth/', include('rest_framework.urls')),
    
    # Path for the main API routes, including chats.urls under 'api/'
    path("api/", include('chats.urls')),
]
