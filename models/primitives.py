"""Small construction helpers; all models remain framework primitives."""
import math

import numpy as np

from core.object3d import Object3D
from geometries import Box, Cylinder, Sphere
from materials import PhongMaterial

INK = (0.055, 0.085, 0.12)
WHITE = (0.82, 0.86, 0.83)
ORANGE = (0.95, 0.29, 0.075)
CYAN = (0.10, 0.83, 0.92)
METAL = PhongMaterial(shininess=56)


def place(parent, obj, position=(0, 0, 0), rotation=(0, 0, 0), emission=0):
    obj.position = np.array(position, dtype=np.float32)
    obj.rotation = np.array(rotation, dtype=np.float32)
    obj.emission = emission
    parent.add(obj)
    return obj


def box(parent, size, position, color=WHITE, rotation=(0, 0, 0), emission=0):
    return place(parent, Box(dimensions=size, color=color, material=METAL),
                 position, rotation, emission)


def cylinder(parent, radius, height, position, color=INK, rotation=(0, 0, 0), segments=20):
    return place(parent, Cylinder(radius=radius, height=height, segments=segments,
                                 color=color, material=METAL), position, rotation)


def sphere(parent, radius, position, color=WHITE, scale=(1, 1, 1), emission=0):
    obj = place(parent, Sphere(radius=radius, segments=16, rings=10,
                              color=color, material=METAL), position, emission=emission)
    obj.scale = np.array(scale, dtype=np.float32)
    return obj


def beam(parent, a, b, thickness=0.08, color=INK):
    """A cylinder aligned between two local endpoints."""
    a, b = np.array(a), np.array(b)
    delta = b - a
    length = float(np.linalg.norm(delta))
    return cylinder(parent, thickness, length, (a + b) / 2, color,
                    (math.acos(float(delta[1] / length)),
                     math.atan2(float(delta[0]), float(delta[2])), 0))


def pivot(parent, position=(0, 0, 0)):
    return place(parent, Object3D(), position)
