import ctypes

#creo una clase(estructura) semejante a la del .dll
class estructura(ctypes.Structure):
    _fields_ = [("a", ctypes.c_int )]

#cargo la librería que he hecho con el visual studio
structdll = ctypes.CDLL ("C:\\Users\\javie\\source\\repos\\structdll\\x64\\Debug\\structdll.dll")

#creo la función en python, sus tipos de argumentos y valor de retorno
funcion = structdll.funcion
funcion.argtypes = [ctypes.POINTER(ctypes.POINTER(estructura))]
funcion.restype = ctypes.c_void_p

#creo un puntero a la clase estructura y lo inicializo a estructura()!! si no le asigna la dirección 0x00 lo cual es mal
struct = ctypes.POINTER(estructura)(estructura())

#para acceder al contenido del puntero a estructura usar puntero.contents.<variables de la estructura>
print(struct.contents.a)
#paso la estructura por referencia 
funcion(ctypes.byref(struct))
print(struct.contents.a)
