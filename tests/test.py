import ctypes

#cargar la libreria de Win32 (32 bits)
#testdll = ctypes.WinDLL ("C:\\Users\\javie\\source\\repos\\testdll\\Debug\\testdll.dll")
# o de x64 (64 bits)
testdll = ctypes.WinDLL ("C:\\Users\\javie\\source\\repos\\testdll\\x64\\Debug\\testdll.dll")

#creo prototipo de funcion indicando el tipo de dato de argumentos
sumarProto = ctypes.WINFUNCTYPE(
    ctypes.c_void_p, #funcion es void
    ctypes.c_int,   #parametros...
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)
#banderas para especificar si el argumento es entrada, salida o entrada por defecto 0 (1,2,4), nombre del argumento y valor por defecto
sumarParams = (1, "x", 0), (1, "y", 0), (1, "c", 0)

#creo la funcion a partir del prototipo indicando en tupla el nombre de la funcion del dll que quiero usar y la libreria de la que viene. además se indican los flags aqui
sumar = sumarProto(("sumar", testdll), sumarParams)

x = ctypes.c_int(2)
y = ctypes.c_int(9)
c = ctypes.c_int(0) #creo el entero

sumar(x, y, ctypes.byref(c))
print(f'{x.value} + {y.value} = {c.value}') #y lo paso por referencia porque la funcion espera recibir un puntero a entero
