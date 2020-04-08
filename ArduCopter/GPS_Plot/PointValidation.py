import numpy as np

def points_in_cylinder(pt1, pt2, r, q):
    vec = pt2 - pt1
    const = r * np.linalg.norm(vec)

    points = np.where(np.dot(q - pt1, vec) >= 0 and np.dot(q - pt2, vec) <= 0 \
                and np.linalg.norm(np.cross(q - pt1, vec)) <= const)

    return len(points[0]) > 0

#From :https://stackoverflow.com/questions/26818772/python-checking-if-a-point-is-in-sphere-with-center-x-y-z/26818848 by - Smit
def inSphere(point, sphere, radius):

    # Calculate the difference between the reference and measuring point
    diff = np.subtract(point, sphere)

    # Calculate square length of vector (distance between ref and point)^2
    dist = np.sum(np.power(diff, 2))

    # If dist is less than radius^2, return True, else return False
    return dist < radius ** 2