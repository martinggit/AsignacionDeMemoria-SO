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

    def asignar(self, proceso, tiempo_actual, t_carga, t_seleccion, t_liberacion):
        self.proceso = proceso
        self.libre = False
        self.t_inicio = tiempo_actual + t_seleccion # No arranca en el arribo, sino recién despues de este tiempo
        self.t_fin = self.t_inicio + proceso.duracion + t_carga + t_liberacion 
        # Tiempo de carga hace que el proceso permanezca más tiempo en memoria 
        # Tiempo de liberacion, cuando un proceso termina, libera recien despues de ese tiempo extra 
        proceso.inicio = self.t_inicio  #instante en que empieza a ejecutarse 
        proceso.asignado = True
        proceso.fin = self.t_fin        #instante en que el proceso termina totalmente (ejecucion + carga + liberación)

        #si un proceso empieza en t=1 y dura 6, ocupa [1,2,3,4,5,6] y queda libre justo en t=7.
        #Así no se pisan los procesos al liberar y reasignar

        #El proceso se asigna en el instante en que llega, pero se ejecuta recién en t_inicio=llegada+t_seleccion
        # t_fin de igual manera, incluye carga y liberación
        # Un proceso recién empieza a usar CPU/Memoria despues del t_seleccion

    def liberar(self):
        self.proceso = None
        self.libre = True
        self.t_inicio = -1
        self.t_fin = -1

    def __repr__(self):
        estado = "Libre" if self.libre else f"Ocupada por {self.proceso.nombre}"
        return f"[Part {self.id}: inicio={self.inicio}, size={self.size}, {estado}]"
