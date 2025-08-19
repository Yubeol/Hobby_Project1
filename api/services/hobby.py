import os, json, time
from pathlib import Path
from string import Template
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except Exception:
    genai = None

GEMINI_KEY = os.getenv('GEMINI_API_KEY', '')

PROMPT_TEMPLATE = Template(r"""
역할: 당신은 한국 사용자의 취미를 '통합 기준'으로 추천하는 코치입니다.
'하나의 추천'은 다음 요소를 모두 반영해야 합니다:
(1) 사용자의 MBTI 성향, (2) 현재 날씨, (3) 위치/반경, (4) 실제 지도 검색에 쓸 수 있는 장소 카테고리 키워드,
(5) 성별 및 건강/제약(비고), (6) 주소(생활권 맥락)

입력:
- MBTI: $mbti
- 성별: $gender
- 현재 날씨: $weather
- 주소: $addr
- 위치: 위도 $lat, 경도 $lon
- 반경: $radius_m m
- 선호(선택): $pref
- 건강/제약(선택): $notes

규칙(아주 중요):
1) JSON ONLY 로 응답. 다른 텍스트 절대 금지.
2) 무조건 'items' 길이는 정확히 3.
3) 각 item은 아래 필드를 반드시 포함:
   - hobby
   - place_keywords (2~3개)
   - why (MBTI/날씨/위치/반경/성별/건강제약/주소를 고려)
   - factors: {"mbti":"…","weather":"…","location":"…","gender":"…","health":"…"}
4) 장소 고유명 금지. '카테고리/종류'로만.
5) 날씨가 나쁘면 실내 위주, 좋으면 실외도 포함.
6) 건강/제약(notes)이 있는 경우 금기 활동 제외 및 저부하 대안 제시.
7) 중복 취미 금지.

이제 실제 입력에 대해 결과만 JSON으로 출력:
""")

def get_hobby_and_keywords(
    mbti: str, weather: str, lat: float, lon: float,
    addr: str = '', radius_m: int = 3000, pref: str = '',
    gender: str = '', notes: str = '', max_retries: int = 3
) -> dict:
    prompt = PROMPT_TEMPLATE.substitute(
        mbti=(mbti or 'unknown'),
        gender=(gender or 'unknown'),
        weather=(weather or 'unknown'),
        lat=f"{lat:.6f}",
        lon=f"{lon:.6f}",
        addr=(addr or 'unknown'),
        radius_m=radius_m,
        pref=(pref or '없음'),
        notes=(notes or '없음')
    )

    if not (GEMINI_KEY and genai):
        return {
            'items': [
                {'hobby': '독서', 'place_keywords': ['도서관', '북카페'], 'why': '키 없음 폴백'},
                {'hobby': '요가', 'place_keywords': ['요가원', '필라테스'], 'why': '키 없음 폴백'},
                {'hobby': '클라이밍', 'place_keywords': ['클라이밍짐'], 'why': '키 없음 폴백'},
            ]
        }

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    gen_cfg = {'response_mime_type':'application/json','temperature':0.7,'top_p':0.9}

    last_err = None
    for _ in range(max_retries):
        try:
            resp = model.generate_content(prompt, generation_config=gen_cfg)
            text = (getattr(resp, 'text', '') or '').strip()
            if not text:
                try:
                    parts = resp.candidates[0].content.parts
                    text = ''.join(getattr(p, 'text', '') for p in parts if getattr(p, 'text', None)).strip()
                except Exception:
                    text = ''
            if not text:
                raise ValueError('Empty response from Gemini')
            data = json.loads(text)
            items = data.get('items', [])
            cleaned = []
            for it in items:
                hobby = (it.get('hobby') or '').strip()
                kws = it.get('place_keywords') or []
                if isinstance(kws, str):
                    kws = [kws]
                kws = [k.strip() for k in kws if isinstance(k, str) and k.strip()]
                why = (it.get('why') or '').strip()
                if hobby and kws:
                    cleaned.append({'hobby': hobby, 'place_keywords': kws, 'why': why})
            if cleaned:
                return {'items': cleaned}
        except Exception as e:
            last_err = e
            time.sleep(1)
    return {'message': f'LLM 실패: {last_err}', 'items': []}
