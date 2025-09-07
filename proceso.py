class Proceso:
    _id_counter = 1  # contador para asignar IDs únicos automáticamente

    def __init__(self, nombre, size, duracion, llegada=0, id=None):
        # Asignar ID automáticamente si no se pasa
        if id is None:
            self.id = Proceso._id_counter
            Proceso._id_counter += 1
        else:
            self.id = id

        self.nombre = nombre        # nombre del proceso
        self.size = size            # tamaño de memoria requerido
        self.duracion = duracion    # tiempo que estará en memoria
        self.llegada = llegada      # instante de arribo
        self.fin = None             #Cambio/el fin depende de cuando lo asignen en memoria
        self.asignado = False
        self.inicio = None

    def __repr__(self):
        return (f"Proceso {{id={self.id}, nombre='{self.nombre}', "
                f"size={self.size}, duracion={self.duracion}, "
                f"llegada={self.llegada}, inicio={self.inicio}, fin={self.fin}}}")
