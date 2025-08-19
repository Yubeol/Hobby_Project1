from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count
from .models import Crew, Review, Post  # 모델 사용

# --- 페이지 렌더 ---
def main(request):
    return render(request, 'main.html')

def community(request):
    return render(request, 'community.html')

def review_new(request):
    return render(request, 'review_new.html')

def review_detail(request, pk):
    return render(request, 'review_detail.html', {'pk': pk})

def review_edit(request, pk):
    return render(request, 'review_edit.html', {'pk': pk})

def board_new(request):
    # 파일명이 border_* 라서 그대로 둠
    return render(request, 'border_new.html')

def board_detail(request, pk):
    return render(request, 'board_detail.html', {'pk': pk})

def board_edit(request, pk):
    return render(request, 'border_edit.html', {'pk': pk})

def notice_detail(request, pk):
    return render(request, 'notice_detail.html', {'pk': pk})

# --- API ---
def best_crews(request):
    """
    메인 BEST 크루: 평점/후기수 기준 상위 4개
    """
    qs = (Crew.objects.filter(status='OPEN')
          .annotate(
              avg_rating=Avg('reviews__rating'),
              review_cnt=Count('reviews', distinct=True)
          )
          .order_by('-avg_rating', '-review_cnt', '-created_at')[:4])

    data = [{
        'id': c.id,
        'title': c.title,
        'cover_image': c.cover_image,
        'avg_rating': round(c.avg_rating or 0, 2),
        'review_cnt': c.review_cnt,
    } for c in qs]
    return JsonResponse(data, safe=False)

def recent_posts(request):
    """
    커뮤니티 최근 글: ?board=REVIEW|FREE|NOTICE (없으면 전체)
    """
    board_code = request.GET.get('board')
    qs = Post.objects.select_related('board', 'user').order_by('-created_at')[:12]
    if board_code:
        qs = qs.filter(board__code=board_code)

    data = [{
        'id': p.id,
        'title': p.title,
        'author': p.user.username,
        'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
        'thumbnail': p.thumbnail,
    } for p in qs]
    return JsonResponse(data, safe=False)
