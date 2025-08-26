def first_fit(particiones, proceso):
    for part in particiones:
        if part.libre and part.size >= proceso.size:
            return part
    return None
