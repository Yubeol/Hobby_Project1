# core/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count
# from .models import Crew, Review, Post  # 모델 만든 경우

# 4-1. 페이지 렌더
def main(request):
    return render(request, 'main.html')

def community(request):
    return render(request, 'community.html')

def review_new(request):      return render(request, 'review_new.html')
def review_detail(request, pk): return render(request, 'review_detail.html', {'pk': pk})
def review_edit(request, pk): return render(request, 'review_edit.html', {'pk': pk})

def board_new(request):       return render(request, 'border_new.html')   # 파일명이 border_*
def board_detail(request, pk): return render(request, 'board_detail.html', {'pk': pk})
def board_edit(request, pk):  return render(request, 'border_edit.html', {'pk': pk})

def notice_detail(request, pk): return render(request, 'notice_detail.html', {'pk': pk})

# 4-2. (선택) 메인 BEST 크루/커뮤니티 목록 API
# def best_crews(request):
#     qs = Crew.objects.filter(status='OPEN') \
#         .annotate(avg_rating=Avg('review__rating'), review_cnt=Count('review')) \
#         .order_by('-avg_rating', '-review_cnt')[:4]
#     data = [{'id': c.id, 'title': c.title, 'cover_image': c.cover_image,
#              'avg_rating': round(c.avg_rating or 0, 2), 'review_cnt': c.review_cnt} for c in qs]
#     return JsonResponse(data, safe=False)

# def recent_posts(request):
#     board = request.GET.get('board')  # 'REVIEW'/'FREE'
#     qs = Post.objects.order_by('-created_at')[:12]
#     data = [{'id': p.id, 'title': p.title} for p in qs]
#     return JsonResponse(data, safe=False)
