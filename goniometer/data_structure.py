'''
This module contains the data structure necessary to store data related to each goniometer axis
'''
import ctypes
from goniometer import OLI

class tagSAFEARRAYBOUND(ctypes.Structure):
    _fields_ = [("cElements", ctypes.c_ulong),
                ("lLbound", ctypes.c_long)]

class tagSAFEARRAY(ctypes.Structure):
    _fields_ = [("cDims",ctypes.c_ushort),
                ("fFeatures",ctypes.c_ushort),
                ("cbElements",ctypes.c_ulong),
                ("cLocks",ctypes.c_ulong),
                ("pvData",ctypes.c_int16 * OLI.MAX_DATA), # This is the array that will contain the values read from the memory buffer associated to a goniometer axis every time it is accessed using OnLineGetData function. Its size is 50 in order to ensure performance, but it can be increased
                ("rgsabound",tagSAFEARRAYBOUND),
                ]