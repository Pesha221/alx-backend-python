from django.contrib import admin
from django.urls import path, include

"api-auth"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),  # All app API routes
    path('api-auth/', include('rest_framework.urls')),  # ⚡ Required for DRF auth
]

