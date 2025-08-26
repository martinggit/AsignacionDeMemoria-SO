def best_fit(particiones, proceso):
    candidatas = [p for p in particiones if p.libre and p.size >= proceso.size]
    if not candidatas:
        return None
    return min(candidatas, key=lambda p: p.size)  # la más ajustada
