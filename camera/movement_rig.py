import numpy as np
import pygame

from core.object3d import Object3D


class MovementRig(Object3D):
    def __init__(
        self,
        move_speed: float = 4.0,
        turn_speed: float = 1.5,
    ) -> None:
        super().__init__()
        self.move_speed = move_speed
        self.turn_speed = turn_speed

    def update(
        self,
        delta_time: float,
        keys: pygame.key.ScancodeWrapper | None = None,
    ) -> None:
        if keys is None:
            super().update(delta_time)
            return

        forward_input = float(keys[pygame.K_w]) - float(keys[pygame.K_s])
        right_input = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
        vertical_input = float(keys[pygame.K_e]) - float(keys[pygame.K_q])

        yaw = float(self.rotation[1])
        forward = np.array(
            [-np.sin(yaw), 0.0, -np.cos(yaw)],
            dtype=np.float32,
        )
        right = np.array(
            [np.cos(yaw), 0.0, -np.sin(yaw)],
            dtype=np.float32,
        )
        movement = forward * forward_input + right * right_input
        movement_length = np.linalg.norm(movement)
        if movement_length > 0.0:
            movement /= movement_length

        self.position += movement * self.move_speed * delta_time
        self.position[1] += vertical_input * self.move_speed * delta_time

        self.rotation[1] += (
            float(keys[pygame.K_LEFT]) - float(keys[pygame.K_RIGHT])
        ) * self.turn_speed * delta_time
        self.rotation[0] += (
            float(keys[pygame.K_DOWN]) - float(keys[pygame.K_UP])
        ) * self.turn_speed * delta_time
        self.rotation[0] = np.clip(self.rotation[0], -1.4, 1.4)
        super().update(delta_time)
