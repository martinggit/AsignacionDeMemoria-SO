from simulador import Simulador
from politicas.first_fit import first_fit

if __name__ == "__main__":
    sim = Simulador(memoria_total=200, archivo_procesos="procesos.json", politica=first_fit)
    sim.correr(tiempo_max=20)
