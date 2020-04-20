#!/usr/bin/env python

#3dPlot libraries
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#My library that parse the logs
import LogUtils as utils
import sys

def data_for_cylinder_along_xy(center_x, center_y, height_z, radius):
    x = np.linspace(0, center_x * 2, 100)
    
    theta = np.linspace(0, 2*np.pi, 100)
    theta_grid, x_grid=np.meshgrid(theta, x)
    
    z_grid = radius*np.sin(theta_grid) + height_z
    y_grid = radius*np.cos(theta_grid) + center_y

    return x_grid,y_grid,z_grid

def data_for_cylinder_along_z(center_x, center_y, height_z, radius):
    z = np.linspace(0, height_z, 100)

    theta = np.linspace(0, 2*np.pi, 50)
    theta_grid, z_grid=np.meshgrid(theta, z)

    x_grid = radius*np.cos(theta_grid) + center_x
    y_grid = radius*np.sin(theta_grid) + center_y

    return x_grid,y_grid,z_grid

#Snippet taken from = https://stackoverflow.com/questions/32317247/how-to-draw-a-cylinder-using-matplotlib-along-length-of-point-x1-y1-and-x2-y2
def data_for_cylinder_along_xy2(origin,end,radius):

    #axis and radius
    p0 = origin
    p1 = end
    R = radius

    #vector in direction of axis
    v = p1 - p0

    #find magnitude of vector
    mag = np.linalg.norm(v)
    
    #unit vector in direction of axis
    v = v / mag
    #make some vector not in the same direction as v
    not_v = np.array([1, 0, 0])
    if (v == not_v).all():
        not_v = np.array([0, 1, 0])

    #make vector perpendicular to v
    n1 = np.cross(v, not_v)

    #normalize n1
    n1 /= np.linalg.norm(n1)
    #make unit vector perpendicular to v and n1
    n2 = np.cross(v, n1)
    #surface ranges over t from 0 to length of axis and 0 to 2*pi
    t = np.linspace(0, mag, 2)
    theta = np.linspace(0, 2 * np.pi, 100)

    #use meshgrid to make 2d arrays
    t, theta = np.meshgrid(t, theta)

    #generate coordinates for surface
    X, Y, Z = [p0[i] + v[i] * t + R * np.sin(theta) * n1[i] + R * np.cos(theta) * n2[i] for i in [0, 1, 2]]

    return X, Y, Z;


def data_for_cylinder_along_xy3(origin,end,radius):

    #axis and radius
    p0 = origin
    p1 = end
    R = radius

    #vector in direction of axis
    v = p1 - p0
    x = np.linspace(0, center_x * 2, 100)
    
    theta = np.linspace(0, 2*np.pi, 100)
    theta_grid, x_grid=np.meshgrid(theta, x)
    
    z_grid = radius*np.sin(theta_grid) + height_z
    y_grid = radius*np.cos(theta_grid) + center_y

    return x_grid,y_grid,z_grid
    mag = np.linalg.norm(v)

    #unit vector in direction of axis
    v = v / mag

    #make some vector not in the same direction as v
    not_v = np.array([1, 0, 0])
    if (v == not_v).all():
        not_v = np.array([0, 1, 0])

    #make vector perpendicular to v
    n1 = np.cross(v, not_v)
    #normalize n1
    n1 /= np.linalg.norm(n1)

    #make unit vector perpendicular to v and n1
    n2 = np.cross(v, n1)

    #surface ranges over t from 0 to length of axis and 0 to 2*pi
    t = np.linspace(0, mag, 200)
    theta = np.linspace(0, 2 * np.pi, 100)
    rsample = np.linspace(0, R, 200)

    #use meshgrid to make 2d arrays
    t, theta2 = np.meshgrid(t, theta)

    rsample,theta = np.meshgrid(rsample, theta)

    #generate coordinates for surface
    # "Tube"
    X, Y, Z = [p0[i] + v[i] * t + R * np.sin(theta2) * n1[i] + R * np.cos(theta2) *       n2[i] for i in [0, 1, 2]]
    return X, Y, Z;

"""
mpl.rcParams['legend.fontsize'] = 10
fig = plt.figure()
ax = fig.gca(projection='3d')

mission = utils.GetMissionWaypoints(sys.argv[1]);

x = []; y = []; z = [];
for waypoint in mission:
    x.append(float(waypoint.x));
    x.append(float(waypoint.x1));
    y.append(float(waypoint.y));
    y.append(float(waypoint.y1));
    z.append(float(waypoint.z));
    z.append(float(waypoint.z1));
    
Xs, Ys, Zs = data_for_cylinder_along_xy2(np.array([x[2], y[2], z[2]]), np.array([x[3], y[3], z[3]]),0.0000001);
ax.plot_surface(Xs, Ys, Zs, alpha=0.2, linewidth=0, color='blue')


Xinner,Yinner,Zinner = data_for_cylinder_along_z( x[2], y[2], 0.0000001,z[2]);



Xout,Yout,Zout = data_for_cylinder_along_z( x[0], y[0], 0.000001111,z[-1]);
ax.plot_surface(Xinner, Yinner, Zinner, alpha=0.4, linewidth=0, color='cyan')
ax.plot_surface(Xout, Yout, Zout, alpha=0.2, linewidth=0, color='blue')
"""
#Xs, Ys, Zs = data_for_cylinder_along_xy2(np.array([x[2], y[2], z[2]]), np.array([x[2], y[3], z[3]]),0.0000001);
#ax.plot_surface(Xs, Ys, Zs, alpha=0.2, linewidth=0, color='blue')

#ax.scatter(x, y, z,label='nice', color='blue', marker='o')
#ax.plot(x, y, z, label=options.missionlabel, color="red");

#for i in range(0,len(x),2):
#    print points_in_cylinder(np.array([x[i], y[i], z[i]]), np.array([x[i+1], y[i+1], z[i+1]]), 0.0000008999,np.array([x[i], y[i], z[i]]));

#Xout,Yout,Zout = data_for_cylinder_along_z( x[0], y[0], z[1], 0.000001111);
#ax.plot_surface(Xout, Yout, Zout, alpha=0.4, linewidth=0, color='cyan')

#Xinner,Yinner,Zinner = data_for_cylinder_along_xy( x[3], y[2], z[2], 0.0000011000);
#ax.plot_surface(Xinner, Yinner, Zinner, alpha=0.8, linewidth=1, color='cyan')

#ax.set_xlabel('Latitude')
#ax.set_ylabel('Longitude')
#ax.set_zlabel('Altitude')

#ax.legend()
#plt.show()