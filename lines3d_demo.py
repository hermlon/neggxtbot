import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import pickle

def load_data(ax, filename):
    calibration = pickle.load(open(filename, 'rb'))
    import pdb; pdb.set_trace()
    for tacholist in calibration:
        ax.plot(tacholist[0], tacholist[1], tacholist[2], label=str(tacholist[0][0]))

mpl.rcParams['legend.fontsize'] = 10
fig = plt.figure()
ax = fig.gca(projection='3d')


load_data(ax, 'calibration_MR.p')
load_data(ax, 'calibration_MM.p')
ax.legend()
plt.show()
