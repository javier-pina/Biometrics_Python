import ctypes


ONLINE_GETERROR		= ctypes.c_int(0)
ONLINE_GETENABLE	= ctypes.c_int(1)	# 1 if specified channel is enabled, 0 if not
ONLINE_GETRATE		= ctypes.c_int(2)	# number of samples per second on the specified channel
ONLINE_GETSAMPLES	= ctypes.c_int(3)	# the number of unread samples on the specified channel
ONLINE_GETVALUE		= ctypes.c_int(4)	# the (current value + 4000) on the specified channel
ONLINE_START		= ctypes.c_int(5)	# start or re-start data transfer
ONLINE_STOP			= ctypes.c_int(6)	# stop data transfer

ONLINE_OK			= ctypes.c_int(0)
ONLINE_COMMSFAIL	= ctypes.c_int(-3)
ONLINE_OVERRUN		= ctypes.c_int(-4)