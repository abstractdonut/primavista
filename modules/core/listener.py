# Listener is a global singleton, since primavista only requires a single
# input port, which should not be opened and closed multiple times. This is
# because opening and closing too many input ports on the same device will cause
# rtmidi to crash.
#
# To access the listener, use
# 
#    import listener
#    listener.listener
#
# For details on how to use the listener, see listenerdef.py.
from modules.core.listenerdef import Listener
listener = Listener()