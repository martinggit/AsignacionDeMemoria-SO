import tkinter as tk
import matplotlib.ticker as ticker
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import os
import random
from simulador import Simulador
from politicas.first_fit import first_fit
from politicas.best_fit import best_fit
from politicas.next_fit import next_fit
from politicas.worst_fit import worst_fit

class InterfazMemoria:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Memoria Dínamica - SO - Martín G.")
        self.root.geometry("1100x700")

        # --- Panel Izquierdo (Controles) ---
        panel = tk.Frame(root, padx=10, pady=10, bg="#f0f0f0", width=300)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False) 

        tk.Label(panel, text="Configuración", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)

        # Inputs
        self.crear_input(panel, "Memoria Total:", "entry_memoria", "500")
        self.crear_input(panel, "T. Carga:", "entry_tcarga", "0")
        self.crear_input(panel, "T. Selección:", "entry_tselec", "0")
        self.crear_input(panel, "T. Liberación:", "entry_tlib", "0")

        # Selector de Estrategia
        tk.Label(panel, text="Estrategia:", bg="#f0f0f0").pack(anchor="w")
        self.combo_algoritmo = ttk.Combobox(panel, values=["First Fit", "Best Fit", "Next Fit", "Worst Fit"])
        self.combo_algoritmo.current(0)
        self.combo_algoritmo.pack(fill=tk.X, pady=5)

        # Selector de Archivo JSON
        tk.Label(panel, text="Archivo Tanda:", bg="#f0f0f0").pack(anchor="w", pady=(10,0))
        self.combo_archivo = ttk.Combobox(panel)
        self.actualizar_archivos()
        self.combo_archivo.pack(fill=tk.X, pady=5)

        tk.Button(panel, text="Refrescar Archivos", command=self.actualizar_archivos).pack(fill=tk.X)

        # Botón Ejecutar
        tk.Button(panel, text="▶ EJECUTAR SIMULACIÓN", bg="#007acc", fg="white", 
                  font=("Arial", 10, "bold"), height=2,
                  command=self.correr_simulacion).pack(fill=tk.X, pady=30)

        # --- Panel Derecho (Gráfico) ---
        self.frame_grafico = tk.Frame(root, bg="white")
        self.frame_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def crear_input(self, parent, label, var_name, default):
        tk.Label(parent, text=label, bg="#f0f0f0").pack(anchor="w")
        entry = tk.Entry(parent)
        entry.insert(0, default)
        entry.pack(fill=tk.X, pady=(0, 10))
        setattr(self, var_name, entry)

    def actualizar_archivos(self):
        # Busca archivos .json en la carpeta actual
        archivos = [f for f in os.listdir(".") if f.endswith(".json")]
        self.combo_archivo['values'] = archivos
        if archivos:
            self.combo_archivo.current(0)

    def correr_simulacion(self):
        try:
            memoria = int(self.entry_memoria.get())
            t_carga = int(self.entry_tcarga.get())
            t_selec = int(self.entry_tselec.get())
            t_lib = int(self.entry_tlib.get())
            archivo = self.combo_archivo.get()
            algoritmo_str = self.combo_algoritmo.get()
        except ValueError:
            messagebox.showerror("Error", "Los campos numéricos deben ser enteros.")
            return

        if not archivo:
            messagebox.showerror("Error", "Selecciona un archivo JSON.")
            return

        mapa_politicas = {
            "First Fit": first_fit,
            "Best Fit": best_fit,
            "Next Fit": next_fit,
            "Worst Fit": worst_fit
        }
        politica_func = mapa_politicas[algoritmo_str]

        try:
            sim = Simulador(
                memoria_total=memoria,
                archivo_procesos=archivo,
                politica=politica_func,
                t_carga=t_carga,
                t_seleccion=t_selec,
                t_liberacion=t_lib
            )
            
            sim.correr()
            
            if not hasattr(sim, 'datos_visuales'):
                messagebox.showerror("Error", "No encontré 'datos_visuales' en el simulador. \n¿Modificaste simulador.py como te indiqué?")
                return

            self.dibujar(sim.datos_visuales, memoria, sim.tiempo)

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error en la simulación:\n{e}")
            print(e) # Para ver el detalle en consola

    def dibujar(self, datos, memoria_total, tiempo_max):
        # Limpiar gráfico anterior para no sobreponer
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        # Crear la figura
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        colores = {} 

        # --- DIBUJAR LOS BLOQUES ---
        for d in datos:
            nombre = d['proceso']
            
            # Generar color si no tiene
            if nombre not in colores:
                colores[nombre] = "#" + ''.join([random.choice('89ABCDEF') for _ in range(6)])

            # Crear rectángulo (x, y, ancho, alto)
            rect = patches.Rectangle(
                (d['inicio_tiempo'], d['inicio_memoria']), 
                d['duracion'], 
                d['tamano_memoria'], 
                linewidth=1, 
                edgecolor='black', 
                facecolor=colores[nombre], 
                alpha=0.8
            )
            ax.add_patch(rect)
            
            # Etiqueta en el centro del bloque
            cx = d['inicio_tiempo'] + d['duracion'] / 2
            cy = d['inicio_memoria'] + d['tamano_memoria'] / 2
            ax.text(cx, cy, nombre, color='black', weight='bold', fontsize=8, ha='center', va='center')

        # --- CONFIGURACIÓN DE EJES ---
        
        # 1. Configurar Eje X (Tiempo): Mostrar CADA unidad (0, 1, 2, 3...)
        ax.set_xlim(0, tiempo_max + 1)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1)) 
        
        # Rotar si son muchos tiempos para que no se encimen
        if tiempo_max > 20:
            ax.tick_params(axis='x', rotation=90, labelsize=8)
        else:
            ax.tick_params(axis='x', labelsize=9)

        # 2. Configurar Eje Y (Memoria): Mostrar de 10 en 10
        ax.set_ylim(0, memoria_total)
        
        # AQUÍ ESTÁ EL CAMBIO CLAVE: Forzado a 10 en 10
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10)) 
        ax.tick_params(axis='y', labelsize=8)

        # 3. Cuadrícula (Grid)
        ax.grid(which='major', color='#CCCCCC', linestyle='-', alpha=0.8)
        
        # Etiquetas y Título
        ax.set_xlabel('Tiempo (u.t.)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Dirección de Memoria (KB)', fontsize=10, fontweight='bold')
        ax.set_title(f"Mapa de Memoria - {self.combo_algoritmo.get()}", fontsize=12)

        # Ajuste de márgenes
        plt.tight_layout()

        # Renderizar en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMemoria(root)
    root.mainloop()