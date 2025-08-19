
import random, math
def _shift(lat, lon, meters):
    # quick lat/lon offset by meters
    dlat = meters / 111_111
    dlon = meters / (111_111 * max(0.1, math.cos(math.radians(lat))))
    return lat + dlat, lon + dlon

def build_crews_for_hobby(hobby: str, lat: float, lon: float, radius_m: int, count: int = 3):
    hobby = hobby or '취미'
    out = []
    for i in range(count):
        r = random.randint(200, min(radius_m, 2000))
        ang = random.random() * 360.0
        dx = r * math.cos(math.radians(ang))
        dy = r * math.sin(math.radians(ang))
        plat, plon = _shift(lat, lon, dy)
        plat, plon = _shift(plat, plon, dx)
        out.append({
            'crew_id': f'{hobby}_{i+1}',
            'title': f'{hobby} 크루 #{i+1}',
            'tagline': '가볍게 함께 해요',
            'when': '토 14:00',
            'duration': '2h',
            'capacity': 8,
            'level': 'beginner',
            'spot': {'name': f'{hobby} 스팟 #{i+1}', 'address': '가까운 곳', 'lat': plat, 'lon': plon},
            'organizer': {'name': '호스트', 'rating': 4.8},
        })
    return out
