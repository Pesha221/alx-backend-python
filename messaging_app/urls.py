from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Interface
    path('admin/', admin.site.urls),
    
    # DRF Login/Logout authentication views
    path('api-auth/', include('rest_framework.urls')),
    
    # Main application API endpoints for the 'chats' app
    # Included at the 'api/' prefix as required by the instruction check.
    path("api/", include('chats.urls')),
]