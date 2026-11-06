import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

G = 9.8  # m/s²


def calcular(radio, v_kmh):
    v_ms = v_kmh / 3.6
    omega = v_ms / radio                      # rad/s
    vc_a = 180 / np.pi * omega              # deg/s
    ac = v_ms ** 2 / radio                    # m/s²
    ac_g = ac / G
    return {
        'Radio (m)': radio,
        'Velocidad (km/h)': v_kmh,
        'Velocidad (m/s)': round(v_ms, 2),
        'Velocidad angular (deg/s)': round(vc_a, 3),
        'Aceleración Centrípeta (m/s2)': round(ac, 3),
        'Aceleración centrípeta en g': round(ac_g, 3),
    }


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movimiento circular: radio, velocidad y Aceleración Centrípeta en g")
        self.geometry("980x600")
        self.minsize(980, 520)

        self.resultados = []  # lista de dicts con los cálculos

        self._crear_entrada()
        self._crear_resultados()
        self._crear_graficas()

    # Primera parte
    def _crear_entrada(self):
        marco = ttk.LabelFrame(self, text="1. Registrar valores")
        marco.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(marco, text="Radio (m):").grid(row=0, column=0, padx=6, pady=8)
        self.ent_radio = ttk.Entry(marco, width=12)
        self.ent_radio.grid(row=0, column=1, padx=6)

        ttk.Label(marco, text="Velocidad (km/h):").grid(row=0, column=2, padx=6)
        self.ent_vel = ttk.Entry(marco, width=12)
        self.ent_vel.grid(row=0, column=3, padx=6)

        ttk.Button(marco, text="Agregar y calcular", command=self.agregar).grid(
            row=0, column=4, padx=10)
        ttk.Button(marco, text="Cargar ejemplo", command=self.cargar_ejemplo).grid(
            row=0, column=5, padx=4)
        
        self.ent_vel.bind("<Return>", lambda e: self.agregar())
        self.ent_radio.bind("<Return>", lambda e: self.ent_vel.focus())
        self.ent_radio.focus()

    # Segunda parte
    def _crear_resultados(self):
        marco = ttk.LabelFrame(self, text="2. Resultados")
        marco.pack(fill="both", expand=True, padx=10, pady=5)

        columnas = ['Radio (m)', 'Velocidad (km/h)', 'Velocidad (m/s)',
                    'Velocidad angular (deg/s)',
                    'Aceleración Centrípeta (m/s2)', 'Aceleración centrípeta en g']
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings",
                                  selectmode="extended")
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=140)

        scroll = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        scroll.pack(side="right", fill="y", pady=6, padx=(0, 6))

        barra = ttk.Frame(self)
        ttk.Button(barra, text="Limpiar todo", command=self.limpiar).pack(side="left", padx=4)
        barra.pack(fill="x", padx=10)
    
    # Tercera parte
    def _crear_graficas(self):
        marco = ttk.LabelFrame(self, text="3. Gráficas")
        marco.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(marco, text="Radio vs Velocidad (color = Aceleración centrípeta en g)",
                   command=self.grafica_scatter).pack(side="left", padx=6, pady=8)
        ttk.Button(marco, text="Aceleración centrípeta en g vs Velocidad",
                   command=self.grafica_g_vs_velocidad).pack(side="left", padx=6)
        ttk.Button(marco, text="Velocidad angular vs Velocidad",
                   command=self.grafica_omega).pack(side="left", padx=6)
        
    # inputs
    def _leer_numero(self, entry, nombre):
        texto = entry.get().strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            raise ValueError(f"'{nombre}' debe ser un número.")
        if valor <= 0:
            raise ValueError(f"'{nombre}' debe ser mayor que cero.")
        return valor

    def agregar(self):
        try:
            radio = self._leer_numero(self.ent_radio, "Radio")
            vel = self._leer_numero(self.ent_vel, "Velocidad")
        except ValueError as err:
            messagebox.showerror("Dato inválido", str(err))
            return
        self._insertar(calcular(radio, vel))
        self.ent_vel.delete(0, tk.END)
        self.ent_radio.focus()

    def _insertar(self, fila):
        self.resultados.append(fila)
        self.tabla.insert("", tk.END, values=list(fila.values()))

    def cargar_ejemplo(self):
        for r in [50.0, 100.0, 200.0]:
            for v in [60.0, 100.0, 120.0]:
                self._insertar(calcular(r, v))

    def _hay_datos(self):
        if not self.resultados:
            messagebox.showwarning("Sin datos", "Primero registra al menos un valor.")
            return False
        return True
    
    def limpiar(self):
        self.resultados.clear()
        self.tabla.delete(*self.tabla.get_children())
    # ---------------------------------------------------------- Gráficas
    def _ventana_grafica(self, titulo):
        ventana = tk.Toplevel(self)
        ventana.title(titulo)
        ventana.geometry("820x600")
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=ventana)
        NavigationToolbar2Tk(canvas, ventana)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return fig, ax, canvas

    def grafica_scatter(self):
        if not self._hay_datos():
            return
        df = pd.DataFrame(self.resultados)
        fig, ax, canvas = self._ventana_grafica("Radio vs Velocidad vs Aceleración centrípeta en g")
        sc = ax.scatter(df['Radio (m)'], df['Velocidad (m/s)'],
                        c=df['Aceleración centrípeta en g'], cmap='plasma', s=120, edgecolor='k')
        fig.colorbar(sc, ax=ax, label='Aceleración centrípeta en g')
        ax.set_title('Relación entre radio, velocidad y aceleración centrípeta en g')
        ax.set_xlabel('Radio de curva (m)')
        ax.set_ylabel('Velocidad (m/s)')
        ax.grid(True)
        fig.tight_layout()
        canvas.draw()

    def grafica_g_vs_velocidad(self):
        if not self._hay_datos():
            return
        df = pd.DataFrame(self.resultados)
        fig, ax, canvas = self._ventana_grafica("Aceleración centrípeta en g vs Velocidad")
        for radio, grupo in df.groupby('Radio (m)'):
            grupo = grupo.sort_values('Velocidad (km/h)')
            ax.plot(grupo['Velocidad (km/h)'], grupo['Aceleración centrípeta en g'],
                    marker='o', label=f'Radio {radio:g} m')
        ax.set_title('Aceleración centrípeta en g según la velocidad')
        ax.set_xlabel('Velocidad (km/h)')
        ax.set_ylabel('Aceleración centrípeta en g')
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        canvas.draw()

    def grafica_omega(self):
        if not self._hay_datos():
            return
        df = pd.DataFrame(self.resultados)
        fig, ax, canvas = self._ventana_grafica("Velocidad angular vs Velocidad")
        for radio, grupo in df.groupby('Radio (m)'):
            grupo = grupo.sort_values('Velocidad (km/h)')
            ax.plot(grupo['Velocidad (km/h)'], grupo['Velocidad angular (deg/s)'],
                    marker='s', label=f'Radio {radio:g} m')
        ax.set_title('Velocidad angular según la velocidad')
        ax.set_xlabel('Velocidad (km/h)')
        ax.set_ylabel('Velocidad angular (deg/s)')
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        canvas.draw()


if __name__ == "__main__":
    App().mainloop()
