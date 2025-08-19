
# Minimal weather helpers (stub). Replace with real API if you want.
def get_weather(lat: float, lon: float):
    # You can integrate a real weather API here. For now, return a generic string.
    return '맑음'
def is_bad_weather(desc: str) -> bool:
    if not desc: return False
    bad_tokens = ['비', '호우', '폭우', '태풍', '폭설']
    return any(tok in desc for tok in bad_tokens)
