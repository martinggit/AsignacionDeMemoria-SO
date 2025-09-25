#Simulador va a manejar la memoria (lista de particiones)
#Leer los procesos desde el json y simular el paso del tiempo según la política elegida

import json
from particion import Particion
from proceso import Proceso

class Simulador:
    def __init__(self, memoria_total, archivo_procesos, politica, t_carga=0, t_seleccion=0, t_liberacion=0, archivo_log="eventos.txt"):
        self.memoria_total = memoria_total
        self.particiones = [Particion(0, memoria_total)]  # arranca con 1 partición libre
        self.procesos = self._cargar_procesos(archivo_procesos)
        self.tiempo = 0
        self.politica = politica
        self.t_carga = t_carga
        self.t_seleccion = t_seleccion
        self.t_liberacion = t_liberacion
        self.pendientes = []  # Cola de espera, si un proceso no entra lo guardo hasta que se libere memoria
        self.archivo_log = archivo_log
        self.ife_total = 0  # índice de fragmentación externa 

        # Lista para procesos en fase de selección/carga (no ocupan memoria todavía)
        self.procesos_en_transicion = []

        # Validar que la memoria sea suficiente para ejecutar la tanda
        self._validar_memoria_suficiente()
        
        with open(self.archivo_log, "w", encoding="utf-8") as f:
            f.write("Simulación de eventos de memoria\n\n") 

    def _validar_memoria_suficiente(self):
        # Verificar que cada proceso individual puede ejecutarse
        for proceso in self.procesos:
            if proceso.size > self.memoria_total:
                print(f"\nERROR: Memoria insuficiente para el proceso {proceso.nombre}")
                print(f"Proceso requiere: {proceso.size} KB")
                print(f"Memoria disponible: {self.memoria_total} KB")
                print("\nLa tanda no puede ejecutarse. Terminando simulación.")
                exit(1)
        
        # Verificar que el primer proceso puede ejecutarse
        if self.procesos:
            primer_proceso = min(self.procesos, key=lambda p: p.llegada)
            if primer_proceso.size > self.memoria_total:
                print(f"\nERROR: El primer proceso ({primer_proceso.nombre}) requiere más memoria que la disponible")
                print(f"Proceso requiere: {primer_proceso.size} KB") 
                print(f"Memoria disponible: {self.memoria_total} KB")
                print("\nSistema batch terminado por memoria insuficiente.")
                exit(1)
        
        print(f"Validación completada: Todos los procesos pueden ejecutarse en {self.memoria_total} KB de memoria") 

    def _log_evento(self, tipo, descripcion):
        with open(self.archivo_log, "a", encoding="utf-8") as f:
            f.write(f"[Tiempo {self.tiempo}] [{tipo}] {descripcion}\n")

    def _log_memoria(self):
        estado = " | ".join(str(p) for p in self.particiones)
        self._log_evento("MEMORIA", f"Estado actual → [{estado}]")

    def _cargar_procesos(self, archivo):
        with open(archivo, "r") as f:
            data = json.load(f)
        procesos = []
        for p in data:
            procesos.append(
                Proceso(
                    nombre=p["nombre"],
                    size=p["size"],
                    duracion=p["duracion"],
                    llegada=p.get("llegada", 0),
                )
            )
        return procesos

    def asignar_particion(self, particion, proceso):
        # si sobra espacio, dividir la partición
        if particion.size > proceso.size:
            nueva = Particion(
                inicio=particion.inicio + proceso.size,
                size=particion.size - proceso.size
            )
            particion.size = proceso.size
            idx = self.particiones.index(particion)
            self.particiones.insert(idx + 1, nueva)

        # Calcular tiempos correctamente
        t_inicio_seleccion = self.tiempo
        t_fin_seleccion = t_inicio_seleccion + self.t_seleccion
        t_fin_carga = t_fin_seleccion + self.t_carga
        t_fin_ejecucion = t_fin_carga + proceso.duracion
        t_fin_liberacion = t_fin_ejecucion + self.t_liberacion

        # evento: selección de partición
        self._log_evento("SELECCIÓN", f"Seleccionada {particion} para {proceso.nombre} (t_sel={self.t_seleccion})")

        # asignar el proceso con los tiempos calculados
        particion.asignar(proceso, t_fin_carga, t_fin_liberacion)
        
        # Agregar a procesos en transición si hay tiempos de selección/carga
        if self.t_seleccion > 0 or self.t_carga > 0:
            self.procesos_en_transicion.append({
                'proceso': proceso,
                'particion': particion,
                't_inicio_memoria': t_fin_carga,
                't_fin_seleccion': t_fin_seleccion
            })
            # La partición se marca como "reservada" pero no ocupa memoria hasta t_fin_carga
            particion.libre = False  # reservada
            particion.ocupando_memoria = False  # no ocupa memoria todavía
        else:
            # Si no hay tiempos adicionales, ocupa memoria inmediatamente
            particion.ocupando_memoria = True
        
        # evento: carga del proceso (cuando realmente empieza a residir en memoria)
        if self.t_carga > 0:
            self._log_evento("CARGA", f"{proceso.nombre} será cargado en t={t_fin_carga} (t_carga={self.t_carga})")
        else:
            self._log_evento("CARGA", f"{proceso.nombre} cargado inmediatamente")
        
        print(f"Asignado {proceso.nombre} en {particion}")
        print(f"→ Datos del proceso {proceso.nombre}: inicio_memoria={t_fin_carga}, fin={t_fin_liberacion}")
        print("Estado de memoria:", self.particiones)
        self._log_evento("ASIGNACIÓN", f"{proceso.nombre} asignado a {particion}")
        self._log_memoria()

    def procesar_transiciones(self):
        # Procesa los procesos que están en fase de selección/carga
        for trans in self.procesos_en_transicion[:]:  # copia para poder modificar la lista
            if self.tiempo == trans['t_inicio_memoria']:
                # El proceso ahora sí ocupa memoria
                trans['particion'].ocupando_memoria = True
                self._log_evento("CARGA_COMPLETADA", f"{trans['proceso'].nombre} ahora ocupa memoria")
                self.procesos_en_transicion.remove(trans)
        
        # Actualizar tiempo actual en particiones para el display
        for p in self.particiones:
            p._tiempo_actual = self.tiempo

    def merge_particiones(self):
        i = 0
        while i < len(self.particiones) - 1:
            actual = self.particiones[i]
            siguiente = self.particiones[i + 1]
            if actual.libre and siguiente.libre:
                # fusionar
                actual.size += siguiente.size
                self.particiones.pop(i + 1)
                self._log_evento("MERGE", f"Se fusionaron particiones libres en {actual}")
            else:
                i += 1
    
    def calcular_memoria_libre(self):
        # Calcula memoria libre considerando procesos en transición (para debug)
        memoria_libre = 0
        for p in self.particiones:
            if p.libre:
                memoria_libre += p.size
            elif not getattr(p, 'ocupando_memoria', True):
                # Partición reservada pero no ocupando memoria todavía
                memoria_libre += p.size
        return memoria_libre
    
    def hay_procesos_activos(self):
        """Verifica si hay procesos ejecutándose o esperando"""
        # Procesos aún no terminados
        procesos_no_terminados = [p for p in self.procesos if p.fin is None or p.fin > self.tiempo]
        # Procesos en cola de espera
        # Procesos en transición
        return len(procesos_no_terminados) > 0 or len(self.pendientes) > 0 or len(self.procesos_en_transicion) > 0

    def correr(self):
        print(f"Simulación iniciada con {len(self.procesos)} procesos.\n")
        while True:
            print(f"\nTiempo: {self.tiempo}")
            print("Estado de memoria:", self.particiones)

            # Procesar transiciones de selección/carga
            self.procesar_transiciones()

            # Liberar procesos terminados
            particiones_a_liberar = [p for p in self.particiones if not p.libre and p.t_fin == self.tiempo]
            for part in particiones_a_liberar:
                if not part.libre and part.t_fin == self.tiempo:
                    print(f"Liberando {part.proceso.nombre} de {part}")
                    self._log_evento("LIBERACIÓN", f"{part.proceso.nombre} liberó {part}")
                    part.liberar()

            # Merge de todas las particiones libres contiguas
            self.merge_particiones()
            self._log_memoria()

            # Llegan procesos en este instante
            for proceso in [p for p in self.procesos if p.llegada == self.tiempo]:
                print(f"Llega {proceso}")
                self._log_evento("LLEGADA", f"Proceso {proceso.nombre} llega al sistema")
                self.pendientes.append(proceso)

            # Reintentar asignar pendientes (batch → FIFO estricto) 
            if self.pendientes:
                proceso = self.pendientes[0]  # el primero que está esperando
                part = self.politica(self.particiones, proceso)
                if part:
                    self.asignar_particion(part, proceso)
                    self.pendientes.pop(0)  # lo saco de la cola

            #I.F.E. = P( memoria no asignada * tiempo que permanece en esa condición). "Mientras haya trabajos esperando parasu ejecución"
            # Calcular IFE si hay procesos esperando
            if self.pendientes or any(p.fin is None for p in self.procesos):
                memoria_libre = self.calcular_memoria_libre()
                print(f"Memoria Libre: {memoria_libre}")
                self.ife_total += memoria_libre
                print(f"IFE acumulado: {self.ife_total}")
                
            # Condición de corte mejorada
            if not self.hay_procesos_activos():
                break

            self.tiempo += 1

        self.merge_particiones()
        print("Estado final de memoria:", self.particiones)
        print("\n Simulación finalizada")
        self._log_evento("FIN", "Simulación finalizada")

        # Calcular estadísticas
        print("\n--- TIEMPOS ---")
        tiempos_retorno = []
        for p in self.procesos:
            if p.fin is not None:
                t_retorno = p.fin - p.llegada
                tiempos_retorno.append(t_retorno)
                print(f"{p.nombre}: Retorno={t_retorno} (Inicio_memoria={p.inicio}, Fin={p.fin}, Llegada={p.llegada})")

        if tiempos_retorno:
            promedio = sum(tiempos_retorno) / len(tiempos_retorno)
            print(f"\nTiempo Medio de Retorno = {promedio:.2f}")

        print(f"Índice de Fragmentación Externa total = {self.ife_total}")
        
        # Tiempo de retorno de la tanda (batch)
        llegada_min = min(p.llegada for p in self.procesos)
        fin_max = max(p.fin for p in self.procesos if p.fin is not None)
        tanda_tr = fin_max - llegada_min
        print(f"\nTiempo de Retorno de la tanda = {tanda_tr}")
        self._log_evento("RESUMEN", f"Tiempo de Retorno de la tanda = {tanda_tr}")