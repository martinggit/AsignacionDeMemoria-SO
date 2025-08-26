from particion import Particion

def first_fit(proceso, particiones, tiempo_actual, t_carga, t_seleccion, t_liberacion):
    for p in particiones:
        if p.libre and p.size >= proceso.size:
            p.asignar(proceso, tiempo_actual, t_carga, t_seleccion, t_liberacion)
            return True
    return False

