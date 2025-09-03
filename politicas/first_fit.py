def first_fit(particiones, proceso):
    for part in particiones:
        if part.libre and part.size >= proceso.size:
            return part
    return None

#First Fit asigna el proceso a la primera partición libre que encuentre recorriendo la memoria desde el principio
#En mi codigo
    #1.Recorre las particiones en orden
    #Va secuencialmente verificando cada partición en la lista particiones.

    #2.Chequea disponibilidad y tamaño
    #Si la partición está libre y su tamaño es mayor o igual al requerido por el proceso, se selecciona.

    #3.Asignación inmediata
    #En cuanto encuentra la primera partición válida, la retorna y corta el recorrido.

    #4.Si no hay espacio
    #Si ninguna partición cumple, el proceso debe esperar.