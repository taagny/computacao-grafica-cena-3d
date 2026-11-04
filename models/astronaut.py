import numpy as np

from core.object3d import Object3D
from geometries import Box, Sphere
from materials import PhongMaterial


class Astronaut(Object3D):
    def __init__(self) -> None:
        super().__init__()
        suit_material = PhongMaterial(
            specular_color=(0.32, 0.35, 0.38),
            shininess=28.0,
        )
        joint_material = PhongMaterial(
            specular_color=(0.4, 0.42, 0.45),
            shininess=36.0,
        )

        torso = Box(
            dimensions=(0.92, 1.05, 0.52),
            color=(0.78, 0.82, 0.84),
            material=suit_material,
        )
        torso.position[1] = 1.48
        self.add(torso)

        chest_panel = Box(
            dimensions=(0.42, 0.38, 0.08),
            color=(0.15, 0.42, 0.56),
            material=joint_material,
        )
        chest_panel.position = np.array([0.0, 1.57, 0.3], dtype=np.float32)
        self.add(chest_panel)

        backpack = Box(
            dimensions=(0.62, 0.82, 0.42),
            color=(0.54, 0.59, 0.63),
            material=joint_material,
        )
        backpack.position = np.array([0.0, 1.48, -0.43], dtype=np.float32)
        self.add(backpack)

        self.body_yaw = 0.0
        self.head_pivot = Object3D()
        self.head_pivot.position[1] = 2.03
        self.add(self.head_pivot)

        helmet = Sphere(
            radius=0.43,
            segments=24,
            rings=16,
            color=(0.84, 0.87, 0.88),
            material=suit_material,
        )
        helmet.scale = np.array([1.0, 1.06, 0.98], dtype=np.float32)
        helmet.position[1] = 0.34
        self.head_pivot.add(helmet)

        visor_rim = Sphere(
            radius=0.32,
            segments=24,
            rings=16,
            color=(0.19, 0.24, 0.29),
            material=joint_material,
        )
        visor_rim.scale = np.array([1.0, 0.76, 0.3], dtype=np.float32)
        visor_rim.position = np.array([0.0, 0.35, 0.34], dtype=np.float32)
        self.head_pivot.add(visor_rim)

        visor = Sphere(
            radius=0.265,
            segments=24,
            rings=16,
            color=(0.07, 0.31, 0.48),
            material=PhongMaterial(
                specular_color=(0.68, 0.78, 0.84),
                shininess=72.0,
            ),
        )
        visor.scale = np.array([1.0, 0.76, 0.28], dtype=np.float32)
        visor.position = np.array([0.0, 0.35, 0.405], dtype=np.float32)
        self.head_pivot.add(visor)

        self.left_arm_pivot = self._create_arm(side=-1.0, material=suit_material)
        self.right_arm_pivot = self._create_arm(side=1.0, material=suit_material)
        self.left_arm_swing = 0.0
        self.right_arm_swing = 0.0
        self.raised_arm_angle = 0.0
        self.arm_swing = 0.0

        self.left_leg_pivot = self._create_leg(side=-1.0, material=suit_material)
        self.right_leg_pivot = self._create_leg(side=1.0, material=suit_material)
        self.leg_swing = 0.0

    def _create_arm(
        self,
        side: float,
        material: PhongMaterial,
    ) -> Object3D:
        shoulder = Object3D()
        shoulder.position = np.array([side * 0.56, 1.82, 0.0], dtype=np.float32)
        self.add(shoulder)

        upper_arm = Box(
            dimensions=(0.3, 0.62, 0.34),
            color=(0.78, 0.82, 0.84),
            material=material,
        )
        upper_arm.position = np.array([side * 0.12, -0.34, 0.0], dtype=np.float32)
        shoulder.add(upper_arm)

        elbow = Object3D()
        elbow.position = np.array([side * 0.12, -0.65, 0.0], dtype=np.float32)
        shoulder.add(elbow)

        forearm = Box(
            dimensions=(0.28, 0.54, 0.32),
            color=(0.78, 0.82, 0.84),
            material=material,
        )
        forearm.position[1] = -0.29
        elbow.add(forearm)

        hand = Sphere(
            radius=0.17,
            segments=16,
            rings=10,
            color=(0.83, 0.85, 0.84),
            material=material,
        )
        hand.scale = np.array([0.92, 1.0, 0.92], dtype=np.float32)
        hand.position[1] = -0.61
        elbow.add(hand)
        return shoulder

    def _create_leg(
        self,
        side: float,
        material: PhongMaterial,
    ) -> Object3D:
        hip = Object3D()
        hip.position = np.array([side * 0.27, 0.96, 0.0], dtype=np.float32)
        self.add(hip)

        thigh = Box(
            dimensions=(0.36, 0.62, 0.4),
            color=(0.74, 0.79, 0.82),
            material=material,
        )
        thigh.position[1] = -0.32
        hip.add(thigh)

        knee = Object3D()
        knee.position[1] = -0.64
        hip.add(knee)

        shin = Box(
            dimensions=(0.32, 0.54, 0.36),
            color=(0.78, 0.82, 0.84),
            material=material,
        )
        shin.position[1] = -0.28
        knee.add(shin)

        boot = Box(
            dimensions=(0.38, 0.2, 0.54),
            color=(0.26, 0.31, 0.36),
            material=PhongMaterial(
                specular_color=(0.25, 0.27, 0.3),
                shininess=20.0,
            ),
        )
        boot.position = np.array([0.0, -0.58, 0.08], dtype=np.float32)
        knee.add(boot)
        return hip

    def set_arm_swing(self, angle: float) -> None:
        self.arm_swing = float(np.clip(angle, -1.0, 1.0))
        self.left_arm_swing = self.arm_swing
        self.right_arm_swing = self.arm_swing
        self.left_arm_pivot.rotation[0] = self.left_arm_swing
        self.right_arm_pivot.rotation[0] = self.right_arm_swing

    def adjust_arm_swing(self, amount: float) -> None:
        self.set_arm_swing(self.arm_swing + amount)

    def set_leg_swing(self, angle: float) -> None:
        self.leg_swing = float(np.clip(angle, -0.8, 0.8))
        self.left_leg_pivot.rotation[0] = self.leg_swing
        self.right_leg_pivot.rotation[0] = -self.leg_swing

    def adjust_leg_swing(self, amount: float) -> None:
        self.set_leg_swing(self.leg_swing + amount)

    def set_raised_arm_angle(self, angle: float) -> None:
        self.raised_arm_angle = float(np.clip(angle, 0.0, np.pi))
        self.right_arm_pivot.rotation[2] = self.raised_arm_angle

    def adjust_raised_arm(self, amount: float) -> None:
        self.set_raised_arm_angle(self.raised_arm_angle + amount)

    def set_head_yaw(self, angle: float) -> None:
        self.head_pivot.rotation[1] = float(np.clip(angle, -1.2, 1.2))

    def adjust_head_yaw(self, amount: float) -> None:
        self.set_head_yaw(self.head_pivot.rotation[1] + amount)

    def set_body_yaw(self, angle: float) -> None:
        self.body_yaw = float(np.clip(angle, -np.pi, np.pi))
        self.rotation[1] = self.body_yaw

    def adjust_body_yaw(self, amount: float) -> None:
        self.set_body_yaw(self.body_yaw + amount)
