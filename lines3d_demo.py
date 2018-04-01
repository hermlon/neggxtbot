import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import pickle
import numpy as np
import math
from random import randint
from gcode_parser import MotorExpFunction

def show_data(ax, calibration):
    for tacholist in calibration:
        ax.plot(tacholist[0], tacholist[1], tacholist[2], label=str(tacholist[0][0]))
    return calibration

mpl.rcParams['legend.fontsize'] = 10
fig = plt.figure()
ax = fig.gca(projection='3d')

# (time, x)
def calc_params(p_1, p_2, n):
    b = math.pow((p_1[0] - n) / (p_2[0] - n), 1 / (p_1[1] - p_2[1]))
    a = (p_1[0] - n) / math.pow(b, p_1[1])
    return (a, b)

calibration_data = pickle.load(open('calibration_MR.p', 'rb'))

# (tacho, power, time)
t_p_1 = (105, 120, 0.0044429075150262745)
t_p_2 = (25, 120, 0.013160743713378907)

p_p_1 = (195, 40, 0.003705470378582294)
p_p_2 = (195, 20, 0.005971569281357985)

n = 0.0029973720892881735

a, b = calc_params((t_p_1[2], t_p_1[0]), (t_p_2[2], t_p_2[0]), n)
c, d = calc_params((p_p_1[2], p_p_1[1]), (p_p_2[2], p_p_2[1]), n)


def fun(x, y):
  return a * math.pow(b, x) + c * math.pow(d, y) + n

x = y = np.arange(0, 200, 5)
X, Y = np.meshgrid(x, y)
zs = np.array([fun(x,y) for x,y in zip(np.ravel(X), np.ravel(Y))])
Z = zs.reshape(X.shape)

ax.plot_surface(X, Y, Z)
show_data(ax, calibration_data)

ax.set_xlabel('X Tacho')
ax.set_ylabel('Y Power')
ax.set_zlabel('Z Time')

print(fun(t_p_1[0], t_p_1[1]) - t_p_1[2])
print(fun(t_p_2[0], t_p_2[1]) - t_p_2[2])
print(fun(p_p_1[0], p_p_1[1]) - p_p_1[2])
print(fun(p_p_2[0], p_p_2[1]) - p_p_2[2])


ax.legend()
plt.show()
