from django.contrib import admin
from django.urls import path, include

'api/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls'))
    
]
