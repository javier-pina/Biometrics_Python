import OLI
import ctypes
from goniometro import OnLineStatus


def getSamplesAvailable(ch):    #ctypes.c_int()
    pStatus = ctypes.c_int32(0)
    OnLineStatus(ch, OLI.ONLINE_GETSAMPLES, ctypes.byref(pStatus))
    return pStatus

def getSampleRate(ch):  #ctypes.c_int()
    pStatus = ctypes.c_int32(0)
    OnLineStatus(ch, OLI.ONLINE_GETRATE, ctypes.byref(pStatus))
    return pStatus


ch = ctypes.c_int(0)
pStatus = getSamplesAvailable(ch)
print(pStatus.value)

pStatus = getSampleRate(ch)
print(pStatus.value)
