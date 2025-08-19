# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class District(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class Crew(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE)
    category    = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    district    = models.ForeignKey(District, null=True, on_delete=models.SET_NULL)
    title       = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cover_image = models.CharField(max_length=255, blank=True)
    capacity    = models.IntegerField(default=0)
    status      = models.CharField(max_length=10, default='OPEN')  # OPEN/CLOSED/HIDDEN
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    def __str__(self): return self.title

class Review(models.Model):
    crew       = models.ForeignKey(Crew, related_name='reviews', on_delete=models.CASCADE)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    rating     = models.PositiveSmallIntegerField()
    content    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Board(models.Model):
    code = models.CharField(max_length=20, unique=True)  # REVIEW/FREE/NOTICE
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class Post(models.Model):
    board      = models.ForeignKey(Board, on_delete=models.CASCADE)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    title      = models.CharField(max_length=150)
    content    = models.TextField()
    thumbnail  = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title
