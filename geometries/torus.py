"""Parametric torus with analytical normals and image UV coordinates."""
import math
import numpy as np
from geometries.base import Geometry


class Torus(Geometry):
    def __init__(self, radius=1.0, tube=0.05, segments=64, sides=8,
                 color=(0.1, 0.8, 0.9), material=None):
        vertices, normals, uvs = [], [], []
        for i in range(segments):
            for j in range(sides):
                for di, dj in ((0, 0), (1, 0), (1, 1), (0, 0), (1, 1), (0, 1)):
                    u, v = (i + di) / segments, (j + dj) / sides
                    a, b = u * math.tau, v * math.tau
                    r = radius + tube * math.cos(b)
                    vertices.append((r * math.cos(a), tube * math.sin(b), r * math.sin(a)))
                    normals.append((math.cos(b) * math.cos(a), math.sin(b), math.cos(b) * math.sin(a)))
                    uvs.append((u, v))
        super().__init__(np.array(vertices, dtype=np.float32), color,
                         np.array(uvs, dtype=np.float32),
                         normals=np.array(normals, dtype=np.float32), material=material)
