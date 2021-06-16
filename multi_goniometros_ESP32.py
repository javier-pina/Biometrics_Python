import ctypes

from sensor_goniometro import biometrics_dll, eje, OLI

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

import bluetooth

import serial

import math


logging.basicConfig( level=logging.DEBUG,
    format='[%(levelname)s] - %(threadName)-10s : %(message)s')


marcas_tiempo = []
paquete = []
añadido_paquete = [0]
guardado = False

###############################################################
#------------------------FUNCIONES-----------------------------
###############################################################
def recoleccion_datos(eje, ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete):     #hacer de esto una funcion y para cada canal crear un hilo?? de momento lo hago con un canal
    logging.debug("lanzado")
    
    muestras = 0
    
    #limpio buffer de ejes
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
        tiempo_goniometro = time.time() - tiempo_inicial

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
            print(ejes[0].dataStructure.contents.cDims)
            print(ejes[0].dataStructure.contents.fFeatures)
            print(ejes[0].dataStructure.contents.cbElements)
            print(ejes[0].dataStructure.contents.cLocks)
            print(list(ejes[0].dataStructure.contents.pvData))
            print(ejes[0].dataStructure.contents.rgsabound.cElements)
            print(ejes[0].dataStructure.contents.rgsabound.lLbound)
            print("--------------------------------------------")
            lock.release()
            """
            
            #muestras += len(list(ejes[0].dataStructure.contents.pvData))

            #cojo el raw output del canal quitando los diez primeros valores que son basura
            raw_output = list(eje.dataStructure.contents.pvData)[10:numberOfSamplesReceived]
            #print(raw_output)

            #hago conversion de todos los valores entre -4000 y 4000 a -180 y 180
            fixed_output = [round(valor*(180/4000), 1) for valor in raw_output if valor in range(-4000,4000)]
            eje.output.extend(fixed_output)

            #hago el fix para mandar al ESP32
            fixed_output_ESP32 = []

            for c in fixed_output:
                fixed_output_ESP32.append( abs(math.floor(c)) )
                fixed_output_ESP32.append( abs(math.floor(100 * (c%1))) )

            lock.acquire()
            if(fixed_output_ESP32):
                paquete.extend(fixed_output_ESP32)
                añadido_paquete[0] += 1

                if(añadido_paquete[0] == 7):
                    socket.send(bytes(paquete))
                    paquete.clear()
                    añadido_paquete[0] = 0  
                    marcas_tiempo.append(tiempo_goniometro)
            lock.release()

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

    if(not guardado):
        my_data_file = open('data.txt', 'w')
        for c in marcas_tiempo:
            my_data_file.write(str(c).replace(".",",",1) + "\r")
            guardado = True

    #si no hay mas muestras que plotear temrinar la recogida de datos y animación
    print("no hay más muestras en el intervalo de tiempo definido")
    
    ani.event_source.stop()
    biblioteca.OnLineStatus(eje.canal, OLI.ONLINE_STOP, ctypes.byref(eje.pStatus))

    #print(f"ángulos: {ejes[0].output}\nmuestras útiles: {len(ejes[0].output)}\nmuestras totales eje 0:{muestras}\ntiempo: {ejes[0].seconds}")
    logging.debug("deteniendo")
    lock.release()

def recoleccion_datos_goniometro(ejes, ani, durationSecs, samplesLeftToPlot):     #hacer de esto una funcion y para cada canal crear un hilo?? de momento lo hago con un canal
    logging.debug("lanzado")
    
    #cojo duracion en segundos y samplesleftoplot
    #durationSecs = int(durationSec_input.get())
    #samplesLeftToPlot = round(ejes[0].sampleRate * durationSecs)   #muestras que quedan dentro del margen de durationSec 

    for eje in ejes:
        #limpio buffer de ejes
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
    
    #time.sleep(0.2)

    
    while samplesLeftToPlot > 0:
        time.sleep(0.01)

        for eje in ejes:
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
    y1 = np.array(ejes[0].output)
    y2 = np.array(ejes[1].output)

    
    y3 = np.array(ejes[2].output)
    y4 = np.array(ejes[3].output)
    
    y5 = np.array(ejes[4].output)
    y6 = np.array(ejes[5].output)
    y7 = np.array(ejes[6].output)
    y8 = np.array(ejes[7].output)
    

    x1 = np.linspace(0, ejes[0].seconds, y1.size)
    x2 = np.linspace(0, ejes[1].seconds, y2.size)

    
    x3 = np.linspace(0, ejes[2].seconds, y3.size)
    x4 = np.linspace(0, ejes[3].seconds, y4.size)
    
    x5 = np.linspace(0, ejes[4].seconds, y5.size)
    x6 = np.linspace(0, ejes[5].seconds, y6.size)
    x7 = np.linspace(0, ejes[6].seconds, y7.size)
    x8 = np.linspace(0, ejes[7].seconds, y8.size)
    

    line1.set_data(x1, y1)
    line2.set_data(x2, y2)

    
    line3.set_data(x3, y3)
    line4.set_data(x4, y4)
    
    line5.set_data(x5, y5)
    line6.set_data(x6, y6)
    line7.set_data(x7, y7)
    line8.set_data(x8, y8)
   


    return line1, line2, line3, line4, line5, line6, line7, line8

    
def comenzar(ejes):
    #cojo duracion en segundos
    durationSecs = int(durationSec_input.get())
    samplesLeftToPlot = round(ejes[0].sampleRate * durationSecs) 

    #preparo plots
    subplot.clear()
    subplot.grid()
    subplot.set_ylim(-180,180)
    subplot.set_xlim(0, durationSecs)
    
    marcas_tiempo.clear()
    guardado = False
    paquete.clear()
    añadido_paquete[0] = 0

    
    uart.write([1])
    tiempo_inicial = time.time()
    
    """
    subplot1.clear()
    subplot1.grid()
    subplot1.set_ylim(-180,180)
    subplot1.set_xlim(0, durationSecs)

    subplot2.clear()
    subplot2.grid()
    subplot2.set_ylim(-180,180)
    subplot2.set_xlim(0, durationSecs)

    subplot3.clear()
    subplot3.grid()
    subplot3.set_ylim(-180,180)
    subplot3.set_xlim(0, durationSecs)
    """

    if threading.active_count() == 1:
        #creo animaciones
        ani = FuncAnimation(f, animate, interval=10, blit=True)
        line1.set_data([], [])
        line2.set_data([], [])

        
        line3.set_data([], [])
        line4.set_data([], [])
        
        line5.set_data([], [])
        line6.set_data([], [])
        line7.set_data([], [])
        line8.set_data([], [])
        
 
        #creo e inicio hilos
        """
        hilo = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([ejes[0], ejes[1]], ani, durationSecs, samplesLeftToPlot))
        hilo.start()
        
        hilo1 = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([ejes[2], ejes[3]], ani, durationSecs, samplesLeftToPlot))
        hilo1.start()
        
        hilo2 = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([ejes[4], ejes[5]], ani, durationSecs, samplesLeftToPlot))
        hilo2.start()
        
        hilo3 = threading.Thread(name="hilo", daemon=True, target=recoleccion_datos_goniometro, args=([ejes[6], ejes[7]], ani, durationSecs, samplesLeftToPlot))
        hilo3.start()
        """

        thread = threading.Thread(name="hilo_canal_0", daemon=True, target=recoleccion_datos, args=(ejes[0], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread.start()
        
        
        thread1 = threading.Thread(name="hilo_canal_1", daemon=True, target=recoleccion_datos, args=(ejes[1], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread1.start()
        

        
        thread2 = threading.Thread(name="hilo_canal_2", daemon=True, target=recoleccion_datos, args=(ejes[2], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread2.start()

        thread3 = threading.Thread(name="hilo_canal_3", daemon=True, target=recoleccion_datos, args=(ejes[3], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread3.start()

        
        thread4 = threading.Thread(name="hilo_canal_4", daemon=True, target=recoleccion_datos, args=(ejes[4], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread4.start()

        thread5 = threading.Thread(name="hilo_canal_5", daemon=True, target=recoleccion_datos, args=(ejes[5], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread5.start()

        thread6 = threading.Thread(name="hilo_canal_6", daemon=True, target=recoleccion_datos, args=(ejes[6], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread6.start()

        thread7 = threading.Thread(name="hilo_canal_7", daemon=True, target=recoleccion_datos, args=(ejes[7], ani, durationSecs, samplesLeftToPlot, tiempo_inicial, guardado, paquete))
        thread7.start()
        
    else:
        print("no ha terminado el experimento anterior")


def hilos():
    print(f"hilos: {threading.enumerate()}")
    print(f"hilo activo: {threading.current_thread()}")

def conexion(s, addr, port):
    try:
        s.getsockname()
        s.close()
        boton_conectar.configure(text = "conectar a ESP32")
    except:
        s.connect((addr,port))
        boton_conectar.configure(text ="Desconectar de ESP32")

###############################################################
#----------------------------UART------------------------------
###############################################################
uart = serial.Serial(
    port='COM5',        
    baudrate=57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    #timeout = 1
)


###############################################################
#------------------------GONIOMETRO----------------------------
###############################################################

ruta_dll = "C:\\Users\\javie\\Desktop\\VSprojects\\goniometros\\OnLineInterface64.dll"
biblioteca = biometrics_dll.Biometrics_dll(ruta_dll)

frecuencia = 100
ejes = [eje.Eje(0, frecuencia), eje.Eje(1,frecuencia), 
        eje.Eje(2, frecuencia), eje.Eje(3,frecuencia),
        eje.Eje(4, frecuencia), eje.Eje(5,frecuencia),
        eje.Eje(6, frecuencia), eje.Eje(7,frecuencia)]

lock = threading.Lock()
hilos = 2
barrier = threading.Barrier(hilos)

print(ejes[0].dataStructure.contents.cDims)
print(ejes[0].dataStructure.contents.fFeatures)
print(ejes[0].dataStructure.contents.cbElements)
print(ejes[0].dataStructure.contents.cLocks)
print(list(ejes[0].dataStructure.contents.pvData))
print(ejes[0].dataStructure.contents.rgsabound.cElements)
print(ejes[0].dataStructure.contents.rgsabound.lLbound)



###############################################################
#-----------------------------TKINTER--------------------------
###############################################################
window = tk.Tk()
matplotlib.use("TkAgg")


#-----------------------------Label y input-----------------------
label_segundos = tk.Label(window, text = "duración experimento (s)")
label_segundos.pack()

durationSec_input = tk.Entry(window)
durationSec_input.pack()
durationSec_input.insert(0,'10')
durationSecs = int(durationSec_input.get())

label_canales = tk.Label(window, text = "número de canales")
label_canales.pack()

canales_input = tk.Entry(window)
canales_input.pack()
canales_input.insert(0,'1')
canales = int(canales_input.get())

socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
socket.settimeout(0.5) 
addr = "7C:9E:BD:92:DB:9E" 
port = 1

#-----------------------------Botones---------------------------
boton = tk.Button(window, text = "comenzar", command = lambda:comenzar(ejes))
boton.pack()

boton_threads = tk.Button(window, text = "threads", command = hilos)
boton_threads.pack()
 

boton_conectar = tk.Button(window, text = "conectar a ESP32", command = lambda:conexion(socket, addr, port))
boton_conectar.pack()


#-----------------------------Figura y plots------------------------
f = Figure(figsize=(5,5), dpi=100)  #creo figura dando tamaño en pulgadas y pixeles por pulgada

#subplot = f.add_subplot(221)  #creo subplots: filas, columnas, índice del subplot actual
subplot = f.add_subplot(111)  #creo subplots: filas, columnas, índice del subplot actual
subplot.grid()
subplot.set_ylim(-180,180)
subplot.set_xlim(0, durationSecs)
line1, = subplot.plot([], [], lw=2, color = "red")
line2, = subplot.plot([], [], lw=2, color = "green")

line3, = subplot.plot([], [], lw=2, color = "blue")
line4, = subplot.plot([], [], lw=2, color = "yellow")

line5, = subplot.plot([], [], lw=2, color = "black")
line6, = subplot.plot([], [], lw=2, color = "orange")

line7, = subplot.plot([], [], lw=2, color = "brown")
line8, = subplot.plot([], [], lw=2, color = "grey")
"""
subplot1 = f.add_subplot(222)  #creo subplots: filas, columnas, índice del subplot actual
subplot1.grid()
subplot1.set_ylim(-180,180)
subplot1.set_xlim(0, durationSecs, durationSecs * 100)
line3, = subplot1.plot([], [], lw=2, color = "red")
line4, = subplot1.plot([], [], lw=2, color = "green")

subplot2 = f.add_subplot(223)  #creo subplots: filas, columnas, índice del subplot actual
subplot2.grid()
subplot2.set_ylim(-180,180)
subplot2.set_xlim(0, durationSecs, durationSecs * 100)
line5, = subplot2.plot([], [], lw=2, color = "red")
line6, = subplot2.plot([], [], lw=2, color = "green")

subplot3 = f.add_subplot(224)  #creo subplots: filas, columnas, índice del subplot actual
subplot3.grid()
subplot3.set_ylim(-180,180)
subplot3.set_xlim(0, durationSecs, durationSecs * 100)
line7, = subplot3.plot([], [], lw=2, color = "red")
line8, = subplot3.plot([], [], lw=2, color = "green")
"""

"""
#------------------------Notebook--------------------------
notebook = ttk.Notebook(window, width=500, height=500)

tab = ttk.Frame(notebook)
notebook.add(tab, text = 'tab')

tab1 = ttk.Frame(notebook)
notebook.add(tab1, text = 'tab1')

notebook.pack(expand=True, fill=tk.BOTH)
"""

#----------------------------Canvas-----------------------------
#canvas = FigureCanvasTkAgg(f, tab)   #creo canvas indicando figura y frame padre
canvas = FigureCanvasTkAgg(f, window)   #creo canvas indicando figura y frame padre
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)  #para ponerlo en la interfaz


window.mainloop()