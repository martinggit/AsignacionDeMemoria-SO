def worst_fit(particiones, proceso):
    candidatas = [p for p in particiones if p.libre and p.size >= proceso.size]
    if not candidatas:
        return None
    return max(candidatas, key=lambda p: p.size)  # la más grande

#Worst Fit siempre asigna el proceso a la partición más grande disponible
#En mi codigo
    #1.Filtra las particiones válidas
    #Selecciona sólo las particiones libres y que tengan suficiente tamaño para el proceso.

    #2.Verifica si hay candidatas
    #Si no hay ninguna, retorna None (proceso no puede asignarse).

    #3.Selecciona la más grande
    #Con max(..., key=lambda p: p.size) elige la partición más grande disponible para asignar el proceso.