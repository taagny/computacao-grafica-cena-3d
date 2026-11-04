import numpy as np

from core.object3d import Object3D
from geometries import Box, Cone, Cylinder, Sphere
from materials import PhongMaterial
from core.texture import Texture
from environment import create_flame_texture


class Rocket(Object3D):
    def __init__(self) -> None:
        super().__init__()
        metal = PhongMaterial(
            specular_color=(0.45, 0.48, 0.52),
            shininess=40.0,
        )
        white_paint = PhongMaterial(
            specular_color=(0.34, 0.34, 0.34),
            shininess=28.0,
        )

        self.body = Cylinder(
            radius=0.58,
            height=2.0,
            segments=32,
            color=(0.82, 0.85, 0.88),
            material=white_paint,
        )
        self.body.position[1] = 1.28
        self.add(self.body)

        nose = Cone(
            radius=0.58,
            height=0.9,
            segments=32,
            color=(0.88, 0.22, 0.16),
            material=PhongMaterial(
                specular_color=(0.42, 0.18, 0.16),
                shininess=36.0,
            ),
        )
        nose.position[1] = 2.73
        self.add(nose)

        engine = Cylinder(
            radius=0.4,
            height=0.28,
            segments=24,
            color=(0.28, 0.32, 0.37),
            material=metal,
        )
        engine.position[1] = 0.14
        self.add(engine)

        window_rim = Sphere(
            radius=0.29,
            segments=20,
            rings=12,
            color=(0.20, 0.24, 0.29),
            material=metal,
        )
        window_rim.scale = np.array([1.0, 1.0, 0.24], dtype=np.float32)
        window_rim.position = np.array([0.0, 1.72, 0.54], dtype=np.float32)
        self.add(window_rim)

        window_glass = Sphere(
            radius=0.22,
            segments=20,
            rings=12,
            color=(0.08, 0.58, 0.78),
            material=PhongMaterial(
                specular_color=(0.65, 0.82, 0.9),
                shininess=72.0,
            ),
        )
        window_glass.scale = np.array([1.0, 1.0, 0.28], dtype=np.float32)
        window_glass.position = np.array([0.0, 1.72, 0.59], dtype=np.float32)
        self.add(window_glass)

        for side in (-1.0, 1.0):
            fin = Box(
                dimensions=(0.16, 0.62, 0.58),
                color=(0.80, 0.20, 0.15),
                material=white_paint,
            )
            fin.position = np.array([side * 0.62, 0.53, 0.0], dtype=np.float32)
            fin.rotation[2] = -side * 0.22
            self.add(fin)

        rear_fin = Box(
            dimensions=(0.16, 0.62, 0.58),
            color=(0.80, 0.20, 0.15),
            material=white_paint,
        )
        rear_fin.position = np.array([0.0, 0.53, -0.62], dtype=np.float32)
        rear_fin.rotation[1] = np.pi / 2.0
        self.add(rear_fin)

        self.left_support_pivot = Object3D()
        self.left_support_pivot.position = np.array(
            [-1.12, 0.95, 0.0],
            dtype=np.float32,
        )
        self.add(self.left_support_pivot)

        self.right_support_pivot = Object3D()
        self.right_support_pivot.position = np.array(
            [1.12, 0.95, 0.0],
            dtype=np.float32,
        )
        self.add(self.right_support_pivot)

        self.left_support = Box(
            dimensions=(0.95, 0.16, 0.18),
            color=(0.70, 0.73, 0.76),
            material=metal,
        )
        self.left_support.position = np.array([0.45, 0.0, 0.0], dtype=np.float32)
        self.left_support_pivot.add(self.left_support)

        self.right_support = Box(
            dimensions=(0.95, 0.16, 0.18),
            color=(0.70, 0.73, 0.76),
            material=metal,
        )
        self.right_support.position = np.array([-0.45, 0.0, 0.0], dtype=np.float32)
        self.right_support_pivot.add(self.right_support)
        self.support_angle = 0.0

        self.flame = Cone(
            radius=0.38,
            height=0.9,
            segments=24,
            texture=Texture(create_flame_texture()),
            material=PhongMaterial(
                specular_color=(1.0, 0.75, 0.25),
                shininess=24.0,
            ),
        )
        self.flame.rotation[2] = np.pi
        self.flame.position[1] = -0.24
        self.add(self.flame)
        self.flame_scale = 0.65
        self.set_flame_scale(self.flame_scale)

    def set_support_angle(self, angle: float) -> None:
        self.support_angle = float(np.clip(angle, 0.0, 1.15))
        self.left_support_pivot.rotation[2] = self.support_angle
        self.right_support_pivot.rotation[2] = -self.support_angle

    def adjust_support_angle(self, amount: float) -> None:
        self.set_support_angle(self.support_angle + amount)

    def set_flame_scale(self, scale: float) -> None:
        self.flame_scale = float(np.clip(scale, 0.2, 1.6))
        self.flame.scale = np.array(
            [
                0.55 * self.flame_scale,
                self.flame_scale,
                0.55 * self.flame_scale,
            ],
            dtype=np.float32,
        )

    def adjust_flame_scale(self, amount: float) -> None:
        self.set_flame_scale(self.flame_scale + amount)
