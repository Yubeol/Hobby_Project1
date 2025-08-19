import io, json, os
from PIL import Image, ImageDraw

from django.http import JsonResponse, HttpResponse, HttpRequest
from rest_framework.decorators import api_view

from .services.hobby import get_hobby_and_keywords
from .services.weather import get_weather, is_bad_weather
from .services.location import reverse_geocode, forward_geocode, search_places_by_keywords
from .services.crew import build_crews_for_hobby


# --------- Helpers ---------
def _float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return float(default)

def _int(v, default=0):
    try:
        return int(v)
    except Exception:
        return int(default)


# --------- Health ---------
@api_view(['GET'])
def health(request: HttpRequest):
    return JsonResponse({'ok': True})


# --------- Hobby recommend (GET + POST) ---------
@api_view(['GET', 'POST'])
def hobby_endpoint(request: HttpRequest):
    data = request.data if request.method == 'POST' else request.GET

    mbti = data.get('mbti', '')
    lat = _float(data.get('lat', 0))
    lon = _float(data.get('lon', 0))
    addr = data.get('addr', '')
    radius_m = _int(data.get('radius_m', 1500))
    weather = data.get('weather', '')
    pref = data.get('pref', '')
    per_keyword_count = _int(data.get('per_keyword_count', 5))
    gender = data.get('gender', '')
    notes = data.get('notes', '')

    # Weather (best-effort)
    try:
        weather = weather or (get_weather(lat, lon) or '정보 없음')
    except Exception:
        weather = '정보 없음'

    # LLM (성별/비고 반영)
    llm = get_hobby_and_keywords(mbti, weather, lat, lon, addr, radius_m, pref, gender, notes)
    items = llm.get('items') or []

    # Bad weather → 실내 보정
    bad = is_bad_weather(weather)
    OUTDOOR_HOBBIES = {'농구', '축구', '러닝', '등산', '자전거', '야외 체육'}
    OUTDOOR_CATS = {'공원', '야외', '야외 코트', '농구장', '축구장', '러닝코스', '자전거길'}
    INDOOR_ALTS = {
        '농구': ['실내 농구장', '실내 체육관', '스포츠센터'],
        '축구': ['실내 풋살', '스포츠센터'],
        '러닝': ['실내 트랙', '헬스장'],
        '등산': ['클라이밍짐'],
        '자전거': ['실내 사이클', '헬스장'],
    }

    filtered = []
    for it in items:
        hobby = (it.get('hobby') or '').strip()
        kws = list(it.get('place_keywords') or [])
        why = (it.get('why') or '').strip()

        if bad:
            if hobby in OUTDOOR_HOBBIES and INDOOR_ALTS.get(hobby):
                kws = INDOOR_ALTS[hobby]
                why = f"{weather}이라 실내로 추천합니다." if not why else f"{why} (날씨:{weather}, 실내로 보정)"
            kws = [k for k in kws if not any(tag in k for tag in OUTDOOR_CATS)]

        if hobby and kws:
            filtered.append({'hobby': hobby, 'place_keywords': kws, 'why': why})

    # 장소 검색
    enriched = []
    source = filtered[:3] if filtered else items[:3]
    for it in source:
        try:
            packs = search_places_by_keywords(it['place_keywords'], lat, lon, radius_m, per_keyword_count)
        except Exception:
            packs = []

        flat = []
        for pack in packs:
            for p in pack.get('places', []):
                name = p.get('name')
                address = p.get('address', '')
                try:
                    plat = float(p.get('lat')); plon = float(p.get('lon'))
                except Exception:
                    continue
                flat.append({
                    'name': name, 'address': address, 'lat': plat, 'lon': plon, 'tel': p.get('tel', '')
                })

        enriched.append({
            'hobby': it['hobby'], 'why': it['why'],
            'places': flat, 'places_by_keyword': packs
        })

    return JsonResponse({
        'ok': True,
        'weather': weather,
        'input': {
            'mbti': mbti, 'lat': lat, 'lon': lon, 'addr': addr,
            'radius_m': radius_m, 'weather': weather, 'pref': pref,
            'per_keyword_count': per_keyword_count, 'gender': gender, 'notes': notes
        },
        'items': enriched
    })


# --------- Crew (mock generator) ---------
@api_view(['GET'])
def crew_endpoint(request: HttpRequest):
    hobby = request.GET.get('hobby', '')
    lat = _float(request.GET.get('lat', 0))
    lon = _float(request.GET.get('lon', 0))
    radius_m = _int(request.GET.get('radius_m', 1500))

    items = build_crews_for_hobby(hobby, lat, lon, radius_m, count=3)
    return JsonResponse({'ok': True, 'hobby': hobby, 'items': items})


# --------- Tmap proxy (stubs if no key) ---------
@api_view(['GET'])
def tmap_reverse(request: HttpRequest):
    lat = _float(request.GET.get('lat', 0))
    lon = _float(request.GET.get('lon', 0))
    return JsonResponse(reverse_geocode(lat, lon))

@api_view(['GET'])
def tmap_forward(request: HttpRequest):
    addr = request.GET.get('addr', '')
    res = forward_geocode(addr)
    if not res:
        return JsonResponse({'ok': False, 'message': '주소→좌표 변환 실패'})
    return JsonResponse({'ok': True, **res})

@api_view(['GET'])
def tmap_search(request: HttpRequest):
    kw = request.GET.get('kw', '')
    lat = _float(request.GET.get('lat', 0))
    lon = _float(request.GET.get('lon', 0))
    radius_m = _int(request.GET.get('radius_m', 1500))
    count = _int(request.GET.get('count', 5))
    packs = search_places_by_keywords([kw], lat, lon, radius_m, count)
    return JsonResponse({'ok': True, 'results': packs})

@api_view(['GET'])
def tmap_staticmap(request: HttpRequest):
    # 키 없어도 항상 동작하는 플레이스홀더 PNG
    w = _int(request.GET.get('width', 512))
    h = _int(request.GET.get('height', 512))
    lat = request.GET.get('lat', '')
    lon = request.GET.get('lon', '')

    img = Image.new('RGB', (max(64, w), max(64, h)), (240, 242, 245))
    draw = ImageDraw.Draw(img)
    text = f"Static Map\nlat={lat}, lon={lon}"
    draw.rectangle(((10, 10), (img.width - 10, img.height - 10)), outline=(100, 100, 120), width=2)
    draw.text((20, 20), text, fill=(20, 20, 20))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')


# --------- Chat endpoints ---------
@api_view(['POST'])
def chat_simple(request: HttpRequest):
    key = os.getenv('GEMINI_API_KEY', '')
    msg = (request.data or {}).get('message', '')
    mbti = (request.data or {}).get('mbti') or '미입력'
    pref = (request.data or {}).get('pref') or '미입력'
    if not key:
        items = [{'hobby': h, 'why': '간단 폴백 추천'} for h in ['보드게임', '클라이밍', '도예 체험']]
        return JsonResponse({'ok': True, 'items': items})

    import google.generativeai as genai
    genai.configure(api_key=key)
    prompt = f"""역할: 한국 사용자의 채팅을 읽고 취미 3개를 추천하는 코치입니다.
- 입력: "{msg}"
- MBTI: {mbti}
- 선호: {pref}
JSON ONLY로 출력. 예: {{"items":[{{"hobby":"독서","why":"집중이 잘됨"}}]}}"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        resp = model.generate_content(prompt, generation_config={'response_mime_type': 'application/json'})
        data = json.loads(getattr(resp, 'text', '') or '{}')
        items = (data.get('items') or [])[:3]
        return JsonResponse({'ok': True, 'items': items})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e), 'items': []})


@api_view(['POST'])
def chat_location(request: HttpRequest):
    # 🔥 프론트에서 성별/비고/주소까지 보낼 수 있게 확장
    body = request.data or {}
    mbti = body.get('mbti') or ''
    pref = body.get('pref') or ''
    lat = _float(body.get('lat', 0))
    lon = _float(body.get('lon', 0))
    radius_m = _int(body.get('radius_m', 1500))
    gender = body.get('gender', '')
    notes = body.get('notes', '')
    addr = body.get('addr', '')
    weather_hint = body.get('weather', '')

    try:
        weather = weather_hint or (get_weather(lat, lon) or '정보 없음')
    except Exception:
        weather = '정보 없음'

    llm = get_hobby_and_keywords(mbti, weather, lat, lon, addr, radius_m, pref, gender, notes)
    if not llm.get('items'):
        return JsonResponse({'ok': False, 'weather': weather, 'message': '추천이 비어있습니다.', 'items': []})

    enriched = []
    for item in llm['items']:
        kws = item.get('place_keywords') or []
        try:
            packs = search_places_by_keywords(kws, lat, lon, radius_m, 4)
        except Exception:
            packs = []

        flat = []
        for pack in packs:
            for p in pack.get('places', []):
                try:
                    flat.append({
                        'name': p.get('name', ''),
                        'address': p.get('address', ''),
                        'lat': float(p.get('lat')), 'lon': float(p.get('lon')),
                        'tel': p.get('tel', '')
                    })
                except Exception:
                    pass

        enriched.append({
            'hobby': item.get('hobby', ''),
            'why': item.get('why', ''),
            'places': flat,
            'places_by_keyword': packs,
        })

    return JsonResponse({'ok': True, 'weather': weather, 'items': enriched})
