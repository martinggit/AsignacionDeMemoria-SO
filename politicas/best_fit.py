def best_fit(particiones, proceso):
    candidatas = [p for p in particiones if p.libre and p.size >= proceso.size]
    if not candidatas:
        return None
    return min(candidatas, key=lambda p: p.size)  # la más ajustada

#Best Fit asigna un proceso al bloque de memoria libre más pequeño posible 
#En mi codigo
    #1.Filtra particiones posibles
    #Se buscan las particiones libres y lo suficientemente grandes para el proceso (p.size >= proceso.size).

    #2.Controla si no hay espacio
    #Si no existe ninguna partición candidata, el proceso debe esperar.

    #3.Selecciona la mejor opción
    #Entre todas las candidatas, se elige la partición con menor tamaño (más ajustada al proceso).

    #4.Resultado
    #Devuelve la partición elegida, luego el simulador la marca como ocupada por el proceso.