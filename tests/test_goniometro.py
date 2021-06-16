import ctypes
import OLI
import matplotlib.pyplot as plt
import time


def fun(ch, sizeMs, pActualSamples):
    pData = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())

    OnLineGetData(ch, sizeMs, ctypes.byref(pData), ctypes.byref(pActualSamples))

    return pData, pActualSamples


#cargar la libreria
OnLineInterface64 = ctypes.CDLL ("c:\\Users\\javie\\Desktop\\VSprojects\\goniometros\\OnLineInterface64.dll")

###############################################################
#------------------------OnlineStatus-------------------------
###############################################################
OnLineStatus = OnLineInterface64.OnLineStatus
OnLineStatus.argtypes = [
    ctypes.c_int,   #ch
    ctypes.c_int,   #statusType
    ctypes.POINTER(ctypes.c_int)    #pStatus
    ]  
OnLineStatus.restype = ctypes.c_long


###############################################################
#------------------------OnlineGetData-------------------------
###############################################################
class tagSAFEARRAYBOUND(ctypes.Structure):
    _fields_ = [("cElements", ctypes.c_ulong),
                ("lLbound", ctypes.c_long)]

class tagSAFEARRAY(ctypes.Structure):
    _fields_ = [("cDims",ctypes.c_ushort),
                ("fFeatures",ctypes.c_ushort),
                ("cbElements",ctypes.c_ulong),
                ("cLocks",ctypes.c_ulong),
                ("pvData",ctypes.c_int16 * 300),
                ("rgsabound",tagSAFEARRAYBOUND),
                ]

OnLineGetData = OnLineInterface64.OnLineGetData
OnLineGetData.argtypes = [
    ctypes.c_int,   #ch
    ctypes.c_int,   #sizeMs
    ctypes.POINTER(ctypes.POINTER(tagSAFEARRAY)),   #pData
    ctypes.POINTER(ctypes.c_int)    #pActualSamples
    ]
OnLineGetData.restype = ctypes.c_long


###############################################################
#---------------------------PRUEBAS----------------------------
###############################################################
#pData = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())

ch = ctypes.c_int(0)    #canal 0 es plano horizontal y 1 plano vertical
sizeMs = ctypes.c_int(4000)  #numberofvalues * 1000 / sample rate
pActualSamples = ctypes.c_int32(0)
pStatus = ctypes.c_int32(0)

#pData.contents.pvData = (ctypes.c_int16 * len(Data))(*Data)


#----------------------LLAMO A FUNCION--------------------
vals = []

OnLineStatus(ch, OLI.ONLINE_GETRATE, ctypes.byref(pStatus))
sampleRate = pStatus.value

durationSecs = 5

SamplesLeftToPlot = int(sampleRate * durationSecs)

OnLineStatus(ch, OLI.ONLINE_START, ctypes.byref(pStatus))
time.sleep(0.1)

pData = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())
#print(f'cDims: {pData.contents.cDims}\nfFeatures: {pData.contents.fFeatures}\ncbElements: {pData.contents.cbElements}\ncLocks: {pData.contents.cLocks}')
#print(f'cElements: {pData.contents.rgsabound.cElements}\nlLbound: {pData.contents.rgsabound.lLbound}')

while SamplesLeftToPlot > 0:
    time.sleep(0.05)

    OnLineStatus(ch, OLI.ONLINE_GETSAMPLES, ctypes.byref(pStatus))
    samples = pStatus.value

    if (samples<0):
        print("error")
        break

    if (samples > 0):
        #LLAMADA A FUNCION
        #pData, pActualSamples = fun(ch, sizeMs, pActualSamples)
        #numberOfSamplesReceived = pActualSamples.value

        
        #LLAMDA A PELO
        print(f'cDims: {pData.contents.cDims}\nfFeatures: {pData.contents.fFeatures}\ncbElements: {pData.contents.cbElements}\ncLocks: {pData.contents.cLocks}')
        print(f'cElements: {pData.contents.rgsabound.cElements}\nlLbound: {pData.contents.rgsabound.lLbound}')
        pData.contents.cDims = 0

        sizeMs.value = int(samples * 1000 / sampleRate)
        OnLineGetData(ch, sizeMs, ctypes.byref(pData), ctypes.byref(pActualSamples))
        numberOfSamplesReceived = pActualSamples.value


        #----------------------MUESTRO RESULTADOS-------------------
        valores = list(pData.contents.pvData)
        valores = valores[10:numberOfSamplesReceived]
        valores_fix = [valor for valor in valores if valor in range(-4000 ,4000)]
        print(valores_fix)

        vals.extend(valores_fix)


        SamplesLeftToPlot = SamplesLeftToPlot - numberOfSamplesReceived


    else: 
        print("sin muestras")


OnLineStatus(ch, OLI.ONLINE_STOP, ctypes.byref(pStatus))

plt.plot(vals)
plt.show()