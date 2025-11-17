from django.contrib import admin
from django.urls import path, include

["api-auth"]
["api/"]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api-auth/', include('rest_framework.urls')),
    path("api/", include('chats.urls')),
]


