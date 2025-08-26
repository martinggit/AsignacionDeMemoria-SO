_last_index = 0

def next_fit(particiones, proceso):
    global _last_index
    n = len(particiones)
    for i in range(n):
        idx = (_last_index + i) % n
        part = particiones[idx]
        if part.libre and part.size >= proceso.size:
            _last_index = idx  # actualizar última posición
            return part
    return None
