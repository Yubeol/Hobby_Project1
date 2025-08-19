
# Stubs for map/geocoding. Replace with real TMAP (or Naver Maps) if desired.
def reverse_geocode(lat: float, lon: float):
    return {'ok': True, 'address': '임시 주소', 'lat': lat, 'lon': lon}
def forward_geocode(addr: str):
    if not addr:
        return None
    # Fake centroid for example
    return {'lat': 37.5665, 'lon': 126.9780}
def search_places_by_keywords(keywords, lat, lon, radius_m, count):
    # Return empty result structure compatible with frontend
    packs = []
    for kw in (keywords or []):
        packs.append({'keyword': kw, 'places': []})
    return packs
