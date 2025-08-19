
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health),
    path('hobby/', views.hobby_endpoint),
    path('crew/', views.crew_endpoint),
    path('tmap/reverse/', views.tmap_reverse),
    path('tmap/forward/', views.tmap_forward),
    path('tmap/search/', views.tmap_search),
    path('tmap/staticmap/', views.tmap_staticmap),
    path('chat/', views.chat_simple),
    path('chat/location/', views.chat_location),
]
