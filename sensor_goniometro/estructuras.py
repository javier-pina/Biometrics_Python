import ctypes


class tagSAFEARRAYBOUND(ctypes.Structure):
    _fields_ = [("cElements", ctypes.c_ulong),
                ("lLbound", ctypes.c_long)]

class tagSAFEARRAY(ctypes.Structure):
    _fields_ = [("cDims",ctypes.c_ushort),
                ("fFeatures",ctypes.c_ushort),
                ("cbElements",ctypes.c_ulong),
                ("cLocks",ctypes.c_ulong),
                ("pvData",ctypes.c_int16 * 20),  #maximo de muestras en buffer si no peta en tiempo real
                ("rgsabound",tagSAFEARRAYBOUND),
                ]