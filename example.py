import numpy as np
import matplotlib.pyplot as plt
import scope_GPIB as scope

scope.list_devices() #only used to show all valid addresses

#myscope=scope.Scope_GPIB(u'GPIB0::1::INSTR', debug=True)
myscope=scope.Scope_GPIB("COM1", debug=False)

x,data=myscope.readScope(fast_mode=False)

plt.plot(x,data)
plt.show()