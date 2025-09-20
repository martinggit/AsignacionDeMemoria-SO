class Particion:
    _id_counter = 1

    def __init__(self, inicio, size, libre=True, proceso=None):
        self.id = Particion._id_counter
        Particion._id_counter += 1
        self.inicio = inicio          # dirección inicial en memoria
        self.size = size              # tamaño de la partición
        self.libre = libre
        self.proceso = proceso
        self.t_inicio = -1
        self.t_fin = -1
        self.ocupando_memoria = True  # Para distinguir entre reservada y ocupando memoria

    def asignar(self, proceso, t_inicio_memoria, t_fin_total):
    
        # Asigna un proceso a la partición
        # t_inicio_memoria: momento en que realmente ocupa memoria (después de selección + carga)
        # t_fin_total: momento en que se libera completamente (después de ejecución + liberación)
        
        self.proceso = proceso
        self.libre = False
        self.t_inicio = t_inicio_memoria  # cuando realmente ocupa memoria
        self.t_fin = t_fin_total  # cuando se libera completamente
        self.t_fin_ejecucion = t_inicio_memoria + proceso.duracion  # cuando termina la ejecución
        self.ocupando_memoria = True  # por defecto, se actualiza en el simulador si hay tiempos
        
        proceso.inicio = t_inicio_memoria  # instante en que empieza a ocupar memoria
        proceso.asignado = True
        proceso.fin = t_fin_total  # instante en que se libera completamente

        # Si un proceso empieza en t=1 y dura 6, ocupa [1,2,3,4,5,6] y queda libre justo en t=7. 
        # Así no se pisan los procesos al liberar y reasignar

    def liberar(self):
        self.proceso = None
        self.libre = True
        self.ocupando_memoria = True
        self.t_inicio = -1
        self.t_fin = -1

    def __repr__(self):
        if self.libre:
            estado = "Libre"
        elif hasattr(self, 'ocupando_memoria') and not self.ocupando_memoria:
            estado = f"Reservada para {self.proceso.nombre}"
        elif hasattr(self, 't_fin_ejecucion') and hasattr(self, 't_inicio') and self.t_inicio != -1:
            # Durante tiempo de liberación
            if hasattr(self, 'proceso') and self.proceso and hasattr(self.proceso, 'duracion'):
                t_actual = getattr(self, '_tiempo_actual', 0)  # Se debe setear desde el simulador
                if t_actual >= self.t_inicio + self.proceso.duracion and t_actual < self.t_fin:
                    estado = f"Liberando {self.proceso.nombre}"
                else:
                    estado = f"Ocupada por {self.proceso.nombre}"
            else:
                estado = f"Ocupada por {self.proceso.nombre}"
        else:
            estado = f"Ocupada por {self.proceso.nombre}"
        return f"[Part {self.id}: inicio={self.inicio}, size={self.size}, {estado}]"

        # Un proceso se seleccion, se carga y luego empieza a estar asignado en memoria. Cuando termina entra el tiempo de liberacion de particion 
        # Ejemplo, t_seleccion=1, t_carga=1 y t_liberacion=1, esos 3 ticks no cuenta como que el proceso está asignado. 
        # Por lo que se deberia contar el IFE en esos 3 ticks y así para cada proceso.