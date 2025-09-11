from simulador import Simulador
from politicas.first_fit import first_fit
from politicas.best_fit import best_fit
from politicas.next_fit import next_fit
from politicas.worst_fit import worst_fit

#Parametros
memoria_total = int(input("Tamaño de memoria disponible: "))

# Mostrar opciones al usuario
print("Seleccione estrategia de asignación de particiones:")
print("1 - first_fit")
print("2 - best_fit")
print("3 - next_fit")
print("4 - worst_fit")

opcion = input("Ingrese el número de la estrategia: ")

politicas = {
    "1": first_fit,
    "2": best_fit,
    "3": next_fit,
    "4": worst_fit
}

politica = politicas.get(opcion)
if politica is None:
    print("Opción no válida, usando first_fit por defecto")
    politica = first_fit

t_carga = int(input("Ingrese tiempo de carga promedio: "))
t_seleccion = int(input("Ingrese tiempo de selección de partición: "))
t_liberacion = int(input("Ingrese tiempo de liberación de partición: "))

archivo = input("Ingrese el nombre de la tanda de procesos (ej: tanda1.json): ")

# Crear y correr simulador
sim = Simulador(
    memoria_total=memoria_total,
    archivo_procesos=archivo,
    politica=politica,
    t_carga = t_carga,
    t_seleccion = t_seleccion,
    t_liberacion = t_liberacion,
)

sim.correr()

