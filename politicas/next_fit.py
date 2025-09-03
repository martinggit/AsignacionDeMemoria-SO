_last_index = 0 # Guarda la última posición de búsqueda en la lista de particiones

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

#Next Fit, variante de First Fit, no arranca desde el inicio de la memoria, sino desde la última posición donde se asignó un proceso
#En mi codigo
    #1.Mantiene el índice de la última búsqueda
    #Usa la variable _last_index para recordar dónde quedó la última asignación.

    #2.Recorrido circular
    #Con (_last_index + i) % n, recorre las particiones a partir de esa posición, y si llega al final vuelve al principio.

    #3.Busca la primera partición adecuada
    #Si encuentra una partición libre con tamaño suficiente, la retorna y actualiza _last_index a esa posición.

    #4.Si no hay lugar
    #Retorna None, indicando que el proceso no puede ser cargado en este instante.