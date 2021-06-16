import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk

import matplotlib.animation as animation
import math
import numpy as np

import threading


#funcion que se repite preiodicamente en el hilo principal
#pongo los datos de los ejes asociados a cada subplot y los devuelvo (necesario por lo del blit)
def animate(i):
    x = np.linspace(0, 10, 1000)
    y = np.sin(2 * np.pi * (x - 0.01 * i))
    print(f"y: {y.size} x: {x.size}")
    line.set_data(x, y)
    return line,

#funcion asociada al boton comenzar de la interfaz, el que comienza la sesón
def comenzar():  
    #creo aquí la animación porque cuando se crea empieza
    #si la creo en el programa principal empieza después de llamar a window.mainloop()  
    ani = animation.FuncAnimation(f, animate, interval=10, blit=True)

    #creo y llamo al hilo que recoge datos de los gonimetros (aqui hace un print nada mas)
    #le tengo que pasar la animación para que se detenga al terminar la recolección de datos
    hilo = threading.Thread(target=loop, args=(5000,ani))
    hilo.start()

#funcion de recolección de datos de goniómetros (aqui un print)
#el argumento i es la iteración actual de la animación
def loop(i, ani):
    print("recogiendo datos...")
    while i>0:
        i-=1
        print(i)
    print("listo")

    ani.event_source.stop()



window = tk.Tk()

f = Figure(figsize=(5,5), dpi=100)  #creo figura dando tamaño en pulgadas y pixeles por pulgada

a = f.add_subplot(211)  #creo subplots: filas, columnas, índice del subplot actual
line, = a.plot([], [], lw=2) #necesito esto para la funcion animacion por lo del blit, devuelvo estado actual de subplot para no sobreescribir datos
a.set_ylim(-1,1)    #pongo límites solamente una vez
a.set_xlim(0,10)

b = f.add_subplot(212)
b.plot([1,2,3,4,5,6,7,8],[3,4,6,7,2,3,4,1])

canvas = FigureCanvasTkAgg(f, window)   #creo canvas indicando figura y frame padre
canvas.draw()   #es como el plot.show()
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)  #para ponerlo en la interfaz

boton = tk.Button(window, text = "comenzar", command = comenzar)
boton.pack()

window.mainloop()

