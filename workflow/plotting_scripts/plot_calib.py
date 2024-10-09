import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from tikzplotlib import save as tikz_save

from matplotlib.lines import Line2D
from matplotlib.legend import Legend
Line2D._us_dashSeq    = property(lambda self: self._dash_pattern[1])
Line2D._us_dashOffset = property(lambda self: self._dash_pattern[0])
Legend._ncol = property(lambda self: self._ncols)

conc = [0.0000, 0.0002,0.0004,0.0006,0.0010,0.0020,0.0040,0.0060]
integral = [2.327907342,5.026148722,9.657281473,11.85617355,18.64290739,36.45568891,76.47733312,111.7382218]

x_prop = [0,1]
y_prop = [0,18761]

fig = plt.figure(figsize=(6, 5))

plt.xlim(0, 0.0060 * 1.05)
plt.ylim(0, 120)

plt.xlabel('Tracer Concentration (g/L)')
plt.ylabel('Integral of Absorbance over Wavelengths (nm)')
plt.grid(True)

plt.scatter(conc, integral, marker='x')
plt.plot(x_prop,y_prop,linestyle="--")

plt.tight_layout()

# plt.show()

## Bug workaround
def tikzplotlib_fix_ncols(obj):
    """
    workaround for matplotlib 3.6 renamed legend's _ncol to _ncols, which breaks tikzplotlib
    """
    if hasattr(obj, "_ncols"):
        obj.f_ncol = obj._ncols
    for child in obj.get_children():
        tikzplotlib_fix_ncols(child)

tikzplotlib_fix_ncols(fig)

tikz_save("./workflow/plotting_scripts/plot.tex")
