import OLI
import ctypes
from goniometro import OnLineStatus, OnLineGetData_init
from getStatus import getSamplesAvailable

def getData(ch, sampleRate, numberOfValues):    #ctypes.c_int, ctypes.c_int, ctypes.c_int
    #llamo a OnLineStatus para coger el número de muestras
    pStatus = getSamplesAvailable(ch)
    print(f'samples available: {pStatus.value}')

    #si hay error, numero de muestras <0 me salgo
    if (pStatus.value < 0):
        if (pStatus.value == OLI.ONLINE_OVERRUN.value):
            print('The Biometrics Analysis buffer has overrun! More than 50000 samples not transferred by MATLAB so stop and re-start the recording.')
        else:
            print('Is the DataLog switched on?')
        return -1,-1, -1
        

    #si numero d emuesstras pedidas es mayor que el de las disponibles se igualan
    if (numberOfValues.value > pStatus.value):
        numberOfValues.value = pStatus.value

    #creo el vector Data que será del tipo [1,2,3,...,numberOfValues] para hacer de eje x en el plot
    Data = []
    for i in range(1,numberOfValues.value+1):
        Data.append(i)

    #creo variable que guardara el número de muestras devueltas por OnLineGetData
    pDataNum = ctypes.c_int32(0)

    #creo funcion OnLineGetData y la estructura values con un array pvData de dimension numberOfValues

    OnLineGetData, tagSAFEARRAY = OnLineGetData_init(numberOfValues)

    values = ctypes.POINTER(tagSAFEARRAY)(tagSAFEARRAY())

    values.contents.cDims = 1
    values.contents.cbElements = 2
    values.contents.cLocks = 0
    values.contents.rgsabound.cElements = numberOfValues.value
    values.contents.rgsabound.lLbound = numberOfValues.value

    #forma de hacer arrays en ctypes ya que quiero meter la lista Data como un array en values.pvData
    #problema! en la estructura tengo definido un array de dimension 0
    #aquí le estoy asignando a ese array otro de dimensión variable
    #solucion, hace funcion con creacion de la estructura que reciba la dimension del array (hecho en goniometro.py)
    #values.contents.pvData = (ctypes.c_int16 * len(Data))(*Data)
    
    #para obtener elementos del array en ctypes lo convierto a lista
    #print(list(values.pvData))

    #creo argumento para OnLineGetData que indica sizeMs
    sizeMs = numberOfValues.value * 1000 / sampleRate.value
    sizeMs = ctypes.c_int(int(sizeMs))

    #llamo a OnLineGetData
    print(list(values.contents.pvData))
    OnLineGetData(ch, sizeMs, ctypes.byref(values), ctypes.byref(pDataNum))

    #obtengo los valores de retorno, número de muestras y array Data para hacer de eje x en plot
    numberOfValues = pDataNum.value

    return numberOfValues, values, Data

