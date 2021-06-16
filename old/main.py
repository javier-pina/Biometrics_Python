import ctypes

from getData import getData

import matplotlib.pyplot as plt
import numpy as np


#llamada a funciones de goniometros
ch = ctypes.c_int(0)
sampleRate  = ctypes.c_int(1000)
numberOfValues = ctypes.c_int(100)

numberOfValues, values, Data = getData(ch, sampleRate, numberOfValues)

print(list(values.contents.pvData))

"""
#plot valores
valor_x = [1,2,3,4,5,6,7]
valor_y = [10,50,40,60,40,50,80]
plt.plot(valor_x, valor_y)
plt.ylabel('eje y')
plt.xlabel('eje x')

#apaño para que el plot no sea bloqueante
plt.show(block=False)

print("hago cosas")

plt.show()
"""