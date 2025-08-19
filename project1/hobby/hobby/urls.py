# hobby/urls.py
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main, name='main'),
    path('community/', views.community, name='community'),
    path('reviews/new/', views.review_new, name='review_new'),
    path('reviews/<int:pk>/', views.review_detail, name='review_detail'),
    path('reviews/<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('boards/new/', views.board_new, name='board_new'),
    path('boards/<int:pk>/', views.board_detail, name='board_detail'),
    path('boards/<int:pk>/edit/', views.board_edit, name='board_edit'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),

    # API(예: 메인 BEST 크루/커뮤니티 목록) – 선택
    path('api/crews/best/', views.best_crews),
    path('api/posts/recent/', views.recent_posts),
]
