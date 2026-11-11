"""Six-wheel explorer: chassis -> suspension -> wheels; mast -> sensor."""
import math
from core.object3d import Object3D
from models.primitives import INK, WHITE, ORANGE, CYAN, box, cylinder, sphere, beam, pivot


class Rover(Object3D):
    WHEEL_RADIUS = 0.38

    def __init__(self):
        super().__init__()
        self.wheels = []
        box(self, (1.6, 0.38, 2.3), (0, 0.98, 0), INK)
        box(self, (1.72, 0.32, 1.9), (0, 1.25, 0), WHITE)
        box(self, (1.78, 0.12, 0.48), (0, 1.46, 0.53), ORANGE)
        box(self, (1.8, 0.10, 0.16), (0, 1.03, 1.22), WHITE)
        box(self, (1.8, 0.10, 0.16), (0, 1.03, -1.22), WHITE)
        for x in (-1.02, 1.02):
            for z in (-0.86, 0, 0.86):
                beam(self, (x * 0.65, 1.0, z * 0.7), (x, 0.40, z), 0.055, WHITE)
                wheel = pivot(self, (x, 0.40, z))
                cylinder(wheel, 0.38, 0.29, (0, 0, 0), INK, (0, 0, math.pi / 2), 24)
                cylinder(wheel, 0.23, 0.31, (0, 0, 0), ORANGE, (0, 0, math.pi / 2))
                cylinder(wheel, 0.11, 0.33, (0, 0, 0), WHITE, (0, 0, math.pi / 2))
                for i in range(12):
                    angle = i * math.tau / 12
                    box(wheel, (0.31, 0.065, 0.095),
                        (0, 0.371 * math.cos(angle), 0.371 * math.sin(angle)),
                        (0.13, 0.17, 0.19), (angle, 0, 0))
                self.wheels.append(wheel)
        # Rear equipment, cooling fins and a pair of solar wings.
        box(self, (0.95, 0.35, 0.58), (0, 1.56, -0.57), INK)
        for i in range(6):
            box(self, (0.045, 0.13, 0.52), (-0.36 + i * 0.14, 1.79, -0.57), WHITE)
        for side in (-1, 1):
            panel = pivot(self, (side * 1.14, 1.50, -0.25))
            panel.rotation[2] = side * 0.16
            box(panel, (0.64, 0.045, 1.45), (0, 0, 0), INK)
            for row in range(6):
                box(panel, (0.55, 0.012, 0.20), (0, 0.031, -0.59 + row * 0.235),
                    (0.09, 0.22, 0.37))
            sphere(self, 0.075, (side * 0.63, 1.23, 1.0), CYAN, emission=0.8)
        cylinder(self, 0.065, 0.82, (0, 1.88, 0.58), WHITE)
        self.sensor = pivot(self, (0, 2.3, 0.58))
        box(self.sensor, (0.78, 0.32, 0.36), (0, 0, 0), WHITE)
        for x in (-0.23, 0.23):
            cylinder(self.sensor, 0.13, 0.09, (x, 0, 0.22), INK, (math.pi / 2, 0, 0))
            sphere(self.sensor, 0.085, (x, 0, 0.28), CYAN, scale=(1, 1, 0.25), emission=0.7)
        beam(self, (-0.56, 1.5, -0.7), (-0.56, 2.35, -0.7), 0.022, WHITE)
        sphere(self, 0.065, (-0.56, 2.35, -0.7), ORANGE, emission=0.6)

    def set_travel(self, distance):
        for wheel in self.wheels:
            wheel.rotation[0] = distance / self.WHEEL_RADIUS
