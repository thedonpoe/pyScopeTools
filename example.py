import numpy as np
import matplotlib.pyplot as plt
import scope

myscope=scope.Scope("COM1",debug=False)

x,data=myscope.readScope()

plt.plot(x,data)
plt.show()