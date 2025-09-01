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
        self.t_inicio = tiempo_actual + t_seleccion
        self.t_fin = self.t_inicio + proceso.duracion + t_carga + t_liberacion
        proceso.inicio = self.t_inicio
        proceso.asignado = True

    def liberar(self):
        self.proceso = None
        self.libre = True
        self.t_inicio = -1
        self.t_fin = -1

    def __repr__(self):
        estado = "Libre" if self.libre else f"Ocupada por {self.proceso.nombre}"
        return f"[Part {self.id}: inicio={self.inicio}, size={self.size}, {estado}]"
