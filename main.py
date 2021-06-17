import ctypes

from goniometer import biometrics_library, axis, OLI

import time

import tkinter as tk 
from tkinter import ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

import threading, logging

import numpy as np


logging.basicConfig( level=logging.DEBUG,
    format='[%(levelname)s] - %(threadName)-10s : %(message)s')



def axis_data_collection(eje, ani, durationSecs, samplesLeftToPlot):     #hacer de esto una funcion y para cada canal crear un hilo?? de momento lo hago con un canal
    logging.debug("lanzado")
    
    muestras = 0
    
    #limpio buffer de axes
    biblioteca.INBIO(eje)

    #inicializa zero samples counter y segundos
    eje.zeroSamplesCounter = 0
    eje.seconds = 0
    
    #barrera para llamar a recoleccion de datos a la vez
    barrier.wait()

    #Start Data Collection to get some data before plotting it
    biblioteca.OnLineStatus(eje.canal, OLI.ONLINE_START, ctypes.byref(eje.pStatus))

    #barrera para reoger datos a la vez

    """
    logging.debug(f"tiempo inicial goniómetros: {tiempo_init_hilo}")
    logging.debug("------------------------------------")
    """
    barrier.wait()
    while samplesLeftToPlot > 0:
        #cojo las muestras disponibles en el buffer
        lock.acquire()
        biblioteca.OnLineStatus(eje.canal, OLI.ONLINE_GETSAMPLES, ctypes.byref(eje.pStatus))
        lock.release()
        eje.samplesInBuffer = eje.pStatus.value

        #error en el buffer puede que se haya desbordado
        if (eje.samplesInBuffer < 0):
            print(f'OnLineStatus ONLINE_GETSAMPLES ha devuelto: {eje.samplesInBuffer}')
            #cerrar todos los plots
            break

        
        #no hay muestras disponibles
        if (eje.samplesInBuffer == 0):
            eje.zeroSamplesCounter += 1
            if (eje.zeroSamplesCounter > 100000):
                print("Estás seguro de haber desactivado el modo de guardar en archivo y que todos los sensores están encendidos?")
                #cerrar todo
                break
        
        #si hay muestras en el buffer...
        if(eje.samplesInBuffer > 10):
            eje.zeroSamplesCounter = 0

            #si hay más muestras (samplesInBuffer) de las que quiero sacar (samplesLeftToPlott)...
            if eje.samplesInBuffer > samplesLeftToPlot:
                eje.samplesInBuffer = samplesLeftToPlot

            if eje.samplesInBuffer > 20: #hago esto porque el vector de pvData es de maximo 25
                eje.samplesInBuffer = 20

            #inicializo variables
            mStoGet = round(eje.samplesInBuffer * 1000 / eje.sampleRate)
            eje.seconds += round(mStoGet/1000, 5)
            eje.samplesInBuffer = round(mStoGet * eje.sampleRate / 1000)
            mStoGet = ctypes.c_int(mStoGet)

            #inicializo estructura de datos
            eje.dataStructure.contents.cDims = 0

            #llamo a onlinegetdata para obtener mediciones
            lock.acquire()
            biblioteca.OnLineGetData(eje.canal, mStoGet, ctypes.byref(eje.dataStructure), ctypes.byref(eje.pDataNum))
            lock.release()
            numberOfSamplesReceived = eje.pDataNum.value
            
            """
            lock.acquire()
            print(axes[0].dataStructure.contents.cDims)
            print(axes[0].dataStructure.contents.fFeatures)
            print(axes[0].dataStructure.contents.cbElements)
            print(axes[0].dataStructure.contents.cLocks)
            print(list(axes[0].dataStructure.contents.pvData))
            print(axes[0].dataStructure.contents.rgsabound.cElements)
            print(axes[0].dataStructure.contents.rgsabound.lLbound)
            print("--------------------------------------------")
            lock.release()
            """
            
            #muestras += len(list(axes[0].dataStructure.contents.pvData))

            #cojo el raw output del canal quitando los diez primeros valores que son basura
            raw_output = list(eje.dataStructure.contents.pvData)[10:numberOfSamplesReceived]
            print(raw_output)

            #hago conversion de todos los valores entre -4000 y 4000 a -180 y 180
            fixed_output = [round(valor*(180/4000), 1) for valor in raw_output if valor in range(-4000,4000)]
            eje.output.extend(fixed_output)


            """
            logging.debug(f"marca de tiempo BT: {tiempo_goniometro}")

            logging.debug(f"ángulos: {fixed_output_ESP32}")
            
            logging.debug("-------------------------------")

            """
            #actualizo el valor de muestras por plotear
            #print(f'samplesInBuffer: {eje.samplesInBuffer}\nsamplesLeftToPlot: {samplesLeftToPlot}')
            lock.acquire()
            samplesLeftToPlot = samplesLeftToPlot - numberOfSamplesReceived
            lock.release()

    #socket.send(bytes([254]))
    lock.acquire()

    #si no hay mas muestras que plotear temrinar la recogida de datos y animación
    print("no hay más muestras en el intervalo de tiempo definido")
    
    ani.event_source.stop()
    biblioteca.OnLineStatus(eje.canal, OLI.ONLINE_STOP, ctypes.byref(eje.pStatus))

    #print(f"ángulos: {axes[0].output}\nmuestras útiles: {len(axes[0].output)}\nmuestras totales eje 0:{muestras}\ntiempo: {axes[0].seconds}")
    logging.debug("deteniendo")
    lock.release()

def recoleccion_datos_goniometro(axes, ani, durationSecs, samplesLeftToPlot):     #hacer de esto una funcion y para cada canal crear un hilo?? de momento lo hago con un canal
    logging.debug("lanzado")
    
    #cojo duracion en segundos y samplesleftoplot
    #durationSecs = int(durationSec_input.get())
    #samplesLeftToPlot = round(axes[0].sampleRate * durationSecs)   #muestras que quedan dentro del margen de durationSec 

    for eje in axes:
        #limpio buffer de axes
        lock.acquire()
        biblioteca.INBIO(eje)
        lock.release()

        #inicializa zero samples counter y segundos
        eje.zeroSamplesCounter = 0
        eje.seconds = 0
        
        #print(f'cDims: {eje.dataStructure.contents.cDims}\nfFeatures: {eje.dataStructure.contents.fFeatures}\ncbElements: {eje.dataStructure.contents.cbElements}\ncLocks: {eje.dataStructure.contents.cLocks}')
        #print(f'cElements: {eje.dataStructure.contents.rgsabound.cElements}\nlLbound: {eje.dataStructure.contents.rgsabound.lLbound}')

        #Start Data Collection to get some data before plotting it
        lock.acquire()
        biblioteca.OnLineStatus(eje.canal, OLI.ONLINE_START, ctypes.byref(eje.pStatus))
        lock.release()
    
    # while data_collection_state:
    while samplesLeftToPlot > 0:
        for eje in axes:
            #cojo las muestras disponibles en el buffer
            lock.acquire()
            biblioteca.OnLineStatus(eje.canal, OLI.ONLINE_GETSAMPLES, ctypes.byref(eje.pStatus))
            lock.release()
            eje.samplesInBuffer = eje.pStatus.value

            #error en el buffer puede que se haya desbordado
            if (eje.samplesInBuffer < 0):
                print(f'OnLineStatus ONLINE_GETSAMPLES ha devuelto: {eje.samplesInBuffer}')
                #cerrar todos los plots
                break

            #no hay muestras disponibles
            if (eje.samplesInBuffer == 0):
                eje.zeroSamplesCounter += 1
                if (eje.zeroSamplesCounter > 100000):
                    print("Estás seguro de haber desactivado el modo de guardar en archivo y que todos los sensores están encendidos?")
                    #cerrar todo
                    break
            
            #si hay muestras en el buffer...
            else:
                eje.zeroSamplesCounter = 0

                #si hay más muestras (samplesInBuffer) de las que quiero sacar (samplesLeftToPlott)...
                if eje.samplesInBuffer > samplesLeftToPlot:
                    eje.samplesInBuffer = samplesLeftToPlot

                if eje.samplesInBuffer > 25: #hago esto porque el vector de pvData es de maximo 25
                    eje.samplesInBuffer = 25

                #inicializo variables
                mStoGet = round(eje.samplesInBuffer * 1000 / eje.sampleRate)
                eje.seconds += round(mStoGet/1000, 5)
                eje.samplesInBuffer = round(mStoGet * eje.sampleRate / 1000)
                mStoGet = ctypes.c_int(mStoGet)

                #inicializo estructura de datos
                eje.dataStructure.contents.cDims = 0

                #llamo a onlinegetdata para obtener mediciones
                lock.acquire()
                biblioteca.OnLineGetData(eje.canal, mStoGet, ctypes.byref(eje.dataStructure), ctypes.byref(eje.pDataNum))
                lock.release()
                numberOfSamplesReceived = eje.pDataNum.value

                #cojo el raw output del canal quitando los diez primeros valores que son basura
                raw_output = list(eje.dataStructure.contents.pvData)[10:numberOfSamplesReceived]

                #hago conversion de todos los valores entre -4000 y 4000 a -180 y 180
                fixed_output = [round(valor*(180/4000), 1) for valor in raw_output if valor in range(-4000,4000)]

                eje.output.extend(fixed_output)
                
                #actualizo el valor de muestras por plotear
                print(f'samplesInBuffer: {eje.samplesInBuffer}\nsamplesLeftToPlot: {samplesLeftToPlot}')
                lock.acquire()
                samplesLeftToPlot -= numberOfSamplesReceived
                lock.release()
    
    #si no hay mas muestras que plotear temrinar la recogida de datos y animación
    print("no hay más muestras en el intervalo de tiempo definido")
    lock.acquire()
    ani.event_source.stop()
    biblioteca.OnLineStatus(eje.canal, OLI.ONLINE_STOP, ctypes.byref(eje.pStatus))
    lock.release()
    
    #print(f'cDims: {eje.dataStructure.contents.cDims}\nfFeatures: {eje.dataStructure.contents.fFeatures}\ncbElements: {eje.dataStructure.contents.cbElements}\ncLocks: {eje.dataStructure.contents.cLocks}')
    #print(f'cElements: {eje.dataStructure.contents.rgsabound.cElements}\nlLbound: {eje.dataStructure.contents.rgsabound.lLbound}')
    
    #print(threading.enumerate())

    logging.debug("deteniendo")

def animate(i):
    y1 = np.array(axes[0].output)
    y2 = np.array(axes[1].output)

    """
    y3 = np.array(axes[2].output)
    y4 = np.array(axes[3].output)
    y5 = np.array(axes[4].output)
    y6 = np.array(axes[5].output)
    y7 = np.array(axes[6].output)
    y8 = np.array(axes[7].output)
    """

    x1 = np.linspace(0, axes[0].seconds, y1.size)
    x2 = np.linspace(0, axes[1].seconds, y2.size)

    """
    x3 = np.linspace(0, axes[2].seconds, y3.size)
    x4 = np.linspace(0, axes[3].seconds, y4.size)
    x5 = np.linspace(0, axes[4].seconds, y5.size)
    x6 = np.linspace(0, axes[5].seconds, y6.size)
    x7 = np.linspace(0, axes[6].seconds, y7.size)
    x8 = np.linspace(0, axes[7].seconds, y8.size)
    """

    line1.set_data(x1, y1)
    line2.set_data(x2, y2)

    """
    line3.set_data(x3, y3)
    line4.set_data(x4, y4)
    line5.set_data(x5, y5)
    line6.set_data(x6, y6)
    line7.set_data(x7, y7)
    line8.set_data(x8, y8)
    """


    return line1, line2,# line3, line4, line5, line6, line7, line8


    
def start_stop_data_collection(axes):
    #cojo duracion en segundos
    durationSecs = int(entry_duration.get())
    samplesLeftToPlot = round(axes[0].sampleRate * durationSecs) 

    #preparo plots
    subplot.clear()
    subplot.grid()
    subplot.set_ylim(-180,180)
    subplot.set_xlim(0, durationSecs)
    
    """
    subplot1.clear()
    subplot1.grid()
    subplot1.set_ylim(-180,180)
    subplot1.set_xlim(0, durationSecs)
    """

    if threading.active_count() == 1:
        #creo animaciones
        ani = FuncAnimation(f, animate, interval=10, blit=True)
        line1.set_data([], [])
        line2.set_data([], [])

        """
        line3.set_data([], [])
        line4.set_data([], [])
        
        line5.set_data([], [])
        line6.set_data([], [])
        line7.set_data([], [])
        line8.set_data([], [])
        """
        
 
        #creo e inicio hilos
        """
        hilo = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([axes[0], axes[1]], ani, durationSecs, samplesLeftToPlot))
        hilo.start()
        
        hilo1 = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([axes[2], axes[3]], ani, durationSecs, samplesLeftToPlot))
        hilo1.start()
        
        hilo2 = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([axes[4], axes[5]], ani, durationSecs, samplesLeftToPlot))
        hilo2.start()
        
        hilo3 = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([axes[6], axes[7]], ani, durationSecs, samplesLeftToPlot))
        hilo3.start()
        """

        thread = threading.Thread(name="hilo_canal_0", daemon=True, target=recoleccion_datos, args=(axes[0], ani, durationSecs, samplesLeftToPlot))
        thread.start()
        
        
        thread1 = threading.Thread(name="hilo_canal_1", daemon=True, target=recoleccion_datos, args=(axes[1], ani, durationSecs, samplesLeftToPlot))
        thread1.start()
        

        """
        thread2 = threading.Thread(name="hilo_canal_2", daemon=True, target=recoleccion_datos, args=(axes[2], ani, durationSecs, samplesLeftToPlot))
        thread2.start()

        thread3 = threading.Thread(name="hilo_canal_3", daemon=True, target=recoleccion_datos, args=(axes[3], ani, durationSecs, samplesLeftToPlot))
        thread3.start()

        
        thread4 = threading.Thread(name="hilo_canal_4", daemon=True, target=recoleccion_datos, args=(axes[4], ani, durationSecs, samplesLeftToPlot))
        thread4.start()

        thread5 = threading.Thread(name="hilo_canal_5", daemon=True, target=recoleccion_datos, args=(axes[5], ani, durationSecs, samplesLeftToPlot))
        thread5.start()

        thread6 = threading.Thread(name="hilo_canal_6", daemon=True, target=recoleccion_datos, args=(axes[6], ani, durationSecs, samplesLeftToPlot))
        thread6.start()

        thread7 = threading.Thread(name="hilo_canal_7", daemon=True, target=recoleccion_datos, args=(axes[7], ani, durationSecs, samplesLeftToPlot))
        thread7.start()
        """
        
    else:
        print("no ha terminado el experimento anterior")

###############################################################
#------------------------GONIOMETRO----------------------------
###############################################################

dll_path = "OnLineInterface64.dll"
biblioteca = biometrics_library.Biometrics_library(dll_path)

sample_rate = 100
axes = [axis.Axis(0, sample_rate), axis.Axis(1,sample_rate)]

lock = threading.Lock()
hilos = 2
barrier = threading.Barrier(hilos)

print(axes[0].dataStructure.contents.cDims)
print(axes[0].dataStructure.contents.fFeatures)
print(axes[0].dataStructure.contents.cbElements)
print(axes[0].dataStructure.contents.cLocks)
print(list(axes[0].dataStructure.contents.pvData))
print(axes[0].dataStructure.contents.rgsabound.cElements)
print(axes[0].dataStructure.contents.rgsabound.lLbound)



###############################################################
#-----------------------------TKINTER--------------------------
###############################################################
window = tk.Tk()
matplotlib.use("TkAgg")


#-----------------------------Label y input-----------------------
lbl_duration = tk.Label(window, text = "Experiment duration (s):")
lbl_duration.pack()

entry_duration = tk.Entry(window)
entry_duration.pack()
entry_duration.insert(0,'10')
durationSecs = int(entry_duration.get())


#-----------------------------Botones---------------------------
btn_start = tk.Button(window, text = "START", command = lambda:start_stop_data_collection(axes))
btn_start.pack(pady = 10)

 

#-----------------------------Figura y plots------------------------
f = Figure(figsize=(5,5), dpi=100)  #creo figura dando tamaño en pulgadas y pixeles por pulgada

#subplot = f.add_subplot(221)  #creo subplots: filas, columnas, índice del subplot actual
subplot = f.add_subplot(111)  #creo subplots: filas, columnas, índice del subplot actual
subplot.grid()
subplot.set_ylim(-180,180)
subplot.set_xlim(0, durationSecs)
line1, = subplot.plot([], [], lw=2, color = "red")
line2, = subplot.plot([], [], lw=2, color = "green")

"""
subplot1 = f.add_subplot(222)  #creo subplots: filas, columnas, índice del subplot actual
subplot1.grid()
subplot1.set_ylim(-180,180)
subplot1.set_xlim(0, durationSecs, durationSecs * 100)
line3, = subplot1.plot([], [], lw=2, color = "blue")
line4, = subplot1.plot([], [], lw=2, color = "yellow")
"""


#----------------------------Canvas-----------------------------
canvas = FigureCanvasTkAgg(f, window)   #creo canvas indicando figura y frame padre
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)  #para ponerlo en la interfaz


window.mainloop()