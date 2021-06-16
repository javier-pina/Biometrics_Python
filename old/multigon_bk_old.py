import ctypes
import OLI

import time

import tkinter as tk 
from tkinter import ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class tagSAFEARRAYBOUND(ctypes.Structure):
    _fields_ = [("cElements", ctypes.c_ulong),
                ("lLbound", ctypes.c_long)]

class tagSAFEARRAY(ctypes.Structure):
    _fields_ = [("cDims",ctypes.c_ushort),
                ("fFeatures",ctypes.c_ushort),
                ("cbElements",ctypes.c_ulong),
                ("cLocks",ctypes.c_ulong),
                ("pvData",ctypes.c_int16 * 300),  #maximo de muestras en buffer si no peta en tiempo real
                ("rgsabound",tagSAFEARRAYBOUND),
                ]


###############################################################
#------------------------FUNCIONES-----------------------------
###############################################################
def INBIO(ch, pStatus, pDataNum, sampleRate):   #funcion para vaciar buffer antes de tomar medidas
    #creo puntero a estructura e inicializo
    values = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())
    values.contents.cDims = 1
    values.contents.cbElements = 2
    values.contents.cLocks = 0
    
    #obtengo el numero de muestras disponibles
    OnLineStatus(ch, OLI.ONLINE_GETSAMPLES, ctypes.byref(pStatus))
    samplesInBuffer = pStatus.value

    if(samplesInBuffer < 0):
        print(f'OnLineStatus ONLINE_GETSAMPLES returned: {pStatus.value}')
        
    if(samplesInBuffer == 0):
        print("OnLineStatus ONLINE_GETSAMPLES returned 0. Are you sure that Save to File mode is off and all sensors are switched on?")

    #si hay muestras en el buffer...
    if(samplesInBuffer > 0):
        #inicializo variables y campos de estructura
        mSinBuffer = round(samplesInBuffer * 1000 / sampleRate) #calculo ms y redondeo
        samplesInBuffer = round(mSinBuffer * sampleRate / 1000)    #recalculo muestras con ms redondeados

        #inicializo campos de estructura
        values.contents.rgsabound.cElements = samplesInBuffer
        values.contents.rgsabound.lLbound = samplesInBuffer

        #llamo a onlinegetdata
        OnLineGetData(ch, ctypes.c_int(mSinBuffer), ctypes.byref(values), ctypes.byref(pDataNum))

        print("buffer empty")

    return values

def comenzar(a):
    #get sample rate 
    OnLineStatus(ch, OLI.ONLINE_GETRATE, ctypes.byref(pStatus))
    sampleRate = pStatus.value

    #get data structure for each channel and empty buffer
    #values = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())
    values = INBIO(ch, pStatus, pDataNum, sampleRate)

    #print(f'cDims: {values.contents.cDims}\nfFeatures: {values.contents.fFeatures}\ncbElements: {values.contents.cbElements}\ncLocks: {values.contents.cLocks}')
    #print(f'cElements: {values.contents.rgsabound.cElements}\nlLbound: {values.contents.rgsabound.lLbound}')

    #Start Data Collection
    OnLineStatus(ch, OLI.ONLINE_START, ctypes.byref(pStatus))
    time.sleep(0.2)

    #Plot Figure Data as soon as it arrives
    zeroSamplesCounter = 0
    SamplesLeftToPlot = round(sampleRate * durationSecs)   #muestras que quedan dentro del margen de durationSec 

    a.cla()
    a.grid()
    a.set_ylim(-4000,4000)
    canvas.draw()

    while SamplesLeftToPlot > 0:
        time.sleep(0.05)
        
        #cojo las muestras disponibles en el buffer
        OnLineStatus(ch, OLI.ONLINE_GETSAMPLES, ctypes.byref(pStatus))
        samplesInBuffer = pStatus.value
        print(f'samplesInBuffer: {samplesInBuffer}')

        #error en el buffer puede que se haya desbordado
        if (samplesInBuffer < 0):
            print(f'OnLineStatus ONLINE_GETSAMPLES returned: {pStatus.value}')
            #cerrar todos los plots
            break

        #no hay muestras disponibles
        if (samplesInBuffer == 0):
            zeroSamplesCounter = zeroSamplesCounter + 1
            if (zeroSamplesCounter > 10000):
                print("Are you sure that Save to File mode is off and all sensors are switched on?")
                #cerrar todo
                break
        
        #si hay muestras en el buffer...
        else:
            zeroSamplesCounter = 0

            #si hay más muestras (samplesInBuffer) de las que quiero sacar (SamplesLeftToPlot)...
            if samplesInBuffer > SamplesLeftToPlot:
                samplesInBuffer = SamplesLeftToPlot

            if samplesInBuffer > 300: #hago esto porque el vector de pvData es de maximo 300
                samplesInBuffer = 300


            #inicializo variables
            mStoGet = round(samplesInBuffer * 1000 / sampleRate)
            samplesInBuffer = round(mStoGet * sampleRate / 1000)
            mStoGet = ctypes.c_int(mStoGet)

            #inicializo estructura de datos
            values.contents.cDims = 0

            #llamo a onlinegetdata para obtener mediciones
            OnLineGetData(ch, mStoGet, ctypes.byref(values), ctypes.byref(pDataNum))
            numberOfSamplesReceived = pDataNum.value

            #añado datos a los plots con values.contents.pvData, values1.contents.pvData...
            valores = list(values.contents.pvData)
            valores = valores[10:numberOfSamplesReceived]
            valores_fix = [valor*(180/4000) for valor in valores if valor in range(-4000,4000)]

            #print(valores_fix)

            vals.extend(valores_fix)



            #a.cla()
            #a.set_ylim(-4000,4000)
            #a.set_xlim(0,int(sampleRate * durationSecs))    #modificar esto para que se vean repeticiones o borrar todo
            #a.grid()
            #a.plot(vals)
            #canvas.draw()
            #canvas.flush_events()
            #time.sleep(0.01)

            
            a.cla()
            a.grid()
            a.set_ylim(-180,180)
            a.set_xlim(0, round(sampleRate * durationSecs))
            a.plot(vals)
            canvas.draw() 
            
           

            #actualizo el valor de muestras por plotear
            print(f'samplesInBuffer: {samplesInBuffer}\nSamplesLeftToPlot: {SamplesLeftToPlot}')
            SamplesLeftToPlot = SamplesLeftToPlot - numberOfSamplesReceived


    #si no hay mas muestras que plotear temrinar la recogida de datos
    print("no hay más muestras en el intervalo de tiempo definido")
    OnLineStatus(ch, OLI.ONLINE_STOP, ctypes.byref(pStatus))

    print(f'cDims: {values.contents.cDims}\nfFeatures: {values.contents.fFeatures}\ncbElements: {values.contents.cbElements}\ncLocks: {values.contents.cLocks}')
    print(f'cElements: {values.contents.rgsabound.cElements}\nlLbound: {values.contents.rgsabound.lLbound}')

def testes():
    vals.extend([1000,-1000,3000,-3000])
    a.cla()
    a.grid()
    a.set_ylim(-4000,4000)

    a.plot(vals)

    canvas.draw()

def borrar():
    a.cla()
    a.grid()
    a.set_ylim(-4000,4000)

    canvas.draw()    


###############################################################
#------------------------LIBRERIA DLL--------------------------
###############################################################
try:    
    OnLineInterface64 = ctypes.CDLL ("c:\\Users\\javie\\Desktop\\VSprojects\\goniometros\\OnLineInterface64.dll")

    #------------------------OnlineStatus-------------------------
    OnLineStatus = OnLineInterface64.OnLineStatus
    OnLineStatus.argtypes = [
        ctypes.c_int,   #ch
        ctypes.c_int,   #statusType
        ctypes.POINTER(ctypes.c_int)    #pStatus
        ]  
    OnLineStatus.restype = ctypes.c_long

    #------------------------OnlineGetData-------------------------
    OnLineGetData = OnLineInterface64.OnLineGetData
    OnLineGetData.argtypes = [
        ctypes.c_int,   #ch
        ctypes.c_int,   #sizeMs
        ctypes.POINTER(ctypes.POINTER(tagSAFEARRAY)),   #pData
        ctypes.POINTER(ctypes.c_int)    #pActualSamples
        ]
    OnLineGetData.restype = ctypes.c_long

except:
    OnLineInterface64 = 0
    print("no se pudo cargar la librería. Abre laaplicación de biometrics")

###############################################################
#------------------------MULTIGON------------------------------
###############################################################
durationSecs = 10
ch =  ctypes.c_int(0)
pDataNum = ctypes.c_int32(0)
pStatus = ctypes.c_int32(0)
vals = []


###############################################################
#-----------------------------TKINTER--------------------------
###############################################################
window = tk.Tk()

matplotlib.use("TkAgg")

#-----------------------------Botones---------------------------
boton = tk.Button(window, text = "comenzar", command = lambda:comenzar(a))
boton.pack()

boton1 = tk.Button(window, text = "testes", command = lambda:testes())
boton1.pack()

boton2 = tk.Button(window, text = "borrar", command = lambda:borrar())
boton2.pack()

#-----------------------------Figura y plots------------------------
f = Figure(figsize=(5,5), dpi=100)  #creo figura dando tamaño en pulgadas y pixeles por pulgada

a = f.add_subplot(211)  #creo subplots: filas, columnas, índice del subplot actual
a.set_ylim(-4000,4000)
a.grid()
a.plot([1000,2000,500,400,3000])

b = f.add_subplot(212)  #creo subplots: filas, columnas, índice del subplot actual
b.set_ylim(-4000,4000)
b.grid()

#------------------------Notebook--------------------------
a_notebook = ttk.Notebook(window, width=500, height=500)

a_tab = ttk.Frame(a_notebook)
a_notebook.add(a_tab, text = 'a')

another_tab = ttk.Frame(a_notebook)
a_notebook.add(another_tab, text = 'b')

a_notebook.pack(expand=True, fill=tk.BOTH)


#----------------------------Canvas-----------------------------
canvas = FigureCanvasTkAgg(f, a_tab)   #creo canvas indicando figura y frame padre
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)  #para ponerlo en la interfaz



window.mainloop()