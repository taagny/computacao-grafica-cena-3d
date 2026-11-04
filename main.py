import sys

import numpy as np
import pygame

from core import Renderer, Scene
from camera import Camera, MovementRig
from geometries import Box, Cone, Cylinder, Plane, Sphere


class RotatingBox(Box):
    def __init__(self) -> None:
        super().__init__(dimensions=(1.1, 1.2, 1.1), color=(0.18, 0.62, 0.95))
        self.rotation_velocity = np.array([0.55, 0.85, 0.25], dtype=np.float32)

    def update(self, delta_time: float) -> None:
        self.rotation += self.rotation_velocity * delta_time
        super().update(delta_time)


def main() -> int:
    pygame.init()
    renderer = None
    scene = None

    try:
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

        width, height = 960, 640
        pygame.display.set_mode(
            (width, height),
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE,
        )
        pygame.display.set_caption(
            "Cena 3D - Etapa 2 | WASD move, setas giram, P pausa"
        )

        renderer = Renderer(width, height)
        scene = Scene(background=(0.035, 0.055, 0.12))
        floor = Plane(width=18.0, depth=14.0, color=(0.20, 0.24, 0.32))
        floor.position[1] = -0.72
        scene.add(floor)

        box = RotatingBox()
        box.position = np.array([-3.0, 0.0, 0.0], dtype=np.float32)
        scene.add(box)

        cylinder = Cylinder(
            radius=0.62,
            height=1.5,
            segments=32,
            color=(0.95, 0.48, 0.16),
        )
        cylinder.position = np.array([-1.5, 0.03, 0.0], dtype=np.float32)
        scene.add(cylinder)

        sphere = Sphere(radius=0.72, segments=24, rings=16, color=(0.28, 0.82, 0.55))
        sphere.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        scene.add(sphere)

        cone = Cone(radius=0.7, height=1.6, segments=32, color=(0.92, 0.28, 0.36))
        cone.position = np.array([1.7, 0.08, 0.0], dtype=np.float32)
        scene.add(cone)

        second_box = Box(
            dimensions=(1.2, 1.2, 1.2),
            color=(0.94, 0.78, 0.24),
        )
        second_box.position = np.array([3.5, 0.0, 0.0], dtype=np.float32)
        scene.add(second_box)

        movement_rig = MovementRig(move_speed=4.0, turn_speed=1.5)
        movement_rig.rotation[0] = 0.22
        camera = Camera(field_of_view=0.82, near=0.1, far=100.0)
        camera.position = np.array([0.0, 2.0, 9.0], dtype=np.float32)
        movement_rig.add(camera)

        clock = pygame.time.Clock()
        running = True
        paused = False
        print(
            "Controles: W/S frente/tras; A/D esquerda/direita; "
            "Q/E desce/sobe; setas giram; P pausa; ESC fecha."
        )

        while running:
            real_delta_time = min(clock.tick(60) / 1000.0, 0.1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p:
                        paused = not paused
                        status = "pausada" if paused else "retomada"
                        print(f"Animacao {status}.")
                elif event.type == pygame.VIDEORESIZE:
                    width, height = max(event.w, 1), max(event.h, 1)
                    renderer.resize(width, height)

            animation_delta_time = 0.0 if paused else real_delta_time
            scene.update(animation_delta_time)
            movement_rig.update(real_delta_time, pygame.key.get_pressed())
            renderer.render(scene, camera)
            pygame.display.flip()

        return 0
    except Exception as error:
        print(f"Erro ao executar a cena: {error}", file=sys.stderr)
        return 1
    finally:
        if scene is not None:
            scene.dispose()
        if renderer is not None:
            renderer.dispose()
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
