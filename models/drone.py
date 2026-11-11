"""Quadrotor with four independent rotor pivots and articulated camera."""
import math
from core.object3d import Object3D
from models.primitives import INK, WHITE, ORANGE, CYAN, box, cylinder, sphere, beam, pivot


class Drone(Object3D):
    def __init__(self):
        super().__init__()
        self.rotors = []
        sphere(self, 0.48, (0, 0, 0), WHITE, (1, 0.42, 1.25))
        box(self, (0.52, 0.16, 0.63), (0, 0.16, 0), ORANGE)
        for x in (-0.88, 0.88):
            for z in (-0.76, 0.76):
                beam(self, (x * 0.22, 0, z * 0.25), (x, 0.05, z), 0.07, INK)
                cylinder(self, 0.14, 0.22, (x, 0.1, z), ORANGE)
                rotor = pivot(self, (x, 0.24, z))
                box(rotor, (0.88, 0.025, 0.09), (0, 0, 0), INK)
                box(rotor, (0.09, 0.025, 0.88), (0, 0.005, 0), INK)
                cylinder(rotor, 0.065, 0.06, (0, 0.025, 0), WHITE)
                self.rotors.append(rotor)
                sphere(self, 0.045, (x, 0, z), CYAN, emission=1)
        for x in (-0.38, 0.38):
            beam(self, (x, -0.08, -0.32), (x, -0.48, -0.45), 0.035, WHITE)
            beam(self, (x, -0.08, 0.32), (x, -0.48, 0.45), 0.035, WHITE)
            beam(self, (x, -0.48, -0.60), (x, -0.48, 0.60), 0.04, INK)
        self.gimbal = pivot(self, (0, -0.26, 0.38))
        sphere(self.gimbal, 0.17, (0, 0, 0), INK)
        sphere(self.gimbal, 0.105, (0, -0.04, 0.13), CYAN, (1, 1, 0.4), emission=0.9)

    def set_rotors(self, angle):
        for i, rotor in enumerate(self.rotors):
            rotor.rotation[1] = angle * (1 if i % 2 else -1)
