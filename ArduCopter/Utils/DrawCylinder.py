#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.linalg import norm

import LogUtils as utils
import PointValidation as validation

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def get_cylinder(p0, p1, R = 0.000015):
    #axis and radius
    p0 = np.array(p0)
    p1 = np.array(p1)

    #vector in direction of axis
    v = p1 - p0
    #find magnitude of vector
    mag = norm(v)
    #unit vector in direction of axis
    v = v / mag
    #make some vector not in the same direction as v
    not_v = np.array([1, 0, 0])
    if (v == not_v).all():
        not_v = np.array([0, 1, 0])
    #make vector perpendicular to v
    n1 = np.cross(v, not_v)
    #normalize n1
    n1 /= norm(n1)
    #make unit vector perpendicular to v and n1
    n2 = np.cross(v, n1)
    #surface ranges over t from 0 to length of axis and 0 to 2*pi
    t = np.linspace(0, mag, 100)
    theta = np.linspace(0, 2 * np.pi, 100)

    #use meshgrid to make 2d arrays
    t, theta = np.meshgrid(t, theta)
    #generate coordinates for surface
    X, Y, Z = [p0[i] + v[i] * t + R * np.sin(theta) * n1[i] + R * np.cos(theta) * n2[i] for i in [0, 1, 2]]

    return X, Y, Z


mission = utils.GetMissionWaypoints("../Missions/agraria_complex.txt")
val = validation.Validation()

X = []; Y = []; Z = []
for waypoint in mission:
    if waypoint.x == waypoint.x1 and waypoint.y == waypoint.y1 and waypoint.z == waypoint.z1:
        continue

    X.append(waypoint.x)
    X.append(waypoint.x1)
    Y.append(waypoint.y)
    Y.append(waypoint.y1)
    Z.append(val._meters_to_degrees(float(waypoint.z)))
    Z.append(val._meters_to_degrees(float(waypoint.z1)))


"""
for i in range(len(X)):
    print X[i], " # ", Y[i], " # ", Z[i]

print len(X), range(0,len(X),2)
for i in range(0,len(X),2):

    p0 = [X[i], Y[i], Z[i]]
    p1 = [X[i+1], Y[i+1], Z[i+1]]

    print "####", p0, p1
    A, B, C = get_cylinder(p0, p1, val._MINOR_RADIUS)
    ax.plot_surface(A, B, C, alpha=0.2, cstride = 12, rstride = 12, color = 'green', linewidth=0, shade=True)

    A, B, C = get_cylinder(p0, p1, val._MAJOR_RADIUS)
    ax.plot_surface(A, B, C, alpha=0.2, cstride = 12, rstride = 12, color = 'orange', linewidth=0, shade=True)

ax.plot(X, Y, Z, label="Mission", color="red")

#cstride = 12, rstride = 12,
"""

p0 = [1, 2, 5]
p1 = [3, 20, 5]

A, B, C = get_cylinder(p0, p1, 1.5)
ax.plot_surface(A, B, C, alpha=0.2, cstride = 16, rstride = 16, color = 'green', linewidth=0, shade=True)


A, B, C = get_cylinder(p0, p1, 3)
ax.plot_surface(A, B, C, alpha=0.1, cstride = 12, rstride = 12, color = 'orange', linewidth=0, shade=True)

ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], label="Mission", color="red")


#ax.grid(False)
#plt.axis('off')
plt.show()
