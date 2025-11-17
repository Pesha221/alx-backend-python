from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Interface
    path('admin/', admin.site.urls),
    
    # DRF Login/Logout authentication views (optional, but standard for browsable API)
    path('api-auth/', include('rest_framework.urls')),
    
    # Main application API endpoints for the 'chats' app
    path("api/", include('chats.urls')),
]
