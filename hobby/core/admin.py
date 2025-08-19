from django.contrib import admin
from .models import Category, District, Crew, Review, Board, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "category", "district", "status", "created_at")
    list_filter  = ("status", "category", "district")
    search_fields = ("title", "description")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "crew", "user", "rating", "created_at")
    list_filter  = ("rating",)
    search_fields = ("content",)

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "user", "created_at")
    list_filter  = ("board",)
    search_fields = ("title", "content")
