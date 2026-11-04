import sys

import numpy as np
import pygame

from camera import Camera, MovementRig
from core import Renderer, Scene
from core.light import DirectionalLight
from core.texture import Texture
from environment import create_lunar_texture
from geometries import Box, Plane, Sphere
from materials import LambertMaterial, PhongMaterial
from models import Rocket


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
            "Cena 3D - Etapa 5 | WASD move, 1/2 suportes, 3/4 chama"
        )

        renderer = Renderer(width, height)
        scene = Scene(
            background=(0.025, 0.045, 0.11),
            directional_light=DirectionalLight(
                direction=(-0.55, -1.0, -0.35),
                color=(1.0, 0.88, 0.72),
                ambient_strength=0.28,
            ),
        )

        lunar_texture = Texture(create_lunar_texture())
        floor = Plane(
            width=24.0,
            depth=22.0,
            color=(1.0, 1.0, 1.0),
            texture=lunar_texture,
            uv_tiles=(8.0, 8.0),
            material=LambertMaterial(),
        )
        floor.position[1] = -0.22
        scene.add(floor)

        platform_base = Box(
            dimensions=(4.8, 0.35, 4.8),
            color=(0.18, 0.22, 0.29),
            material=LambertMaterial(),
        )
        platform_base.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        scene.add(platform_base)

        platform_top = Box(
            dimensions=(4.2, 0.12, 4.2),
            color=(0.46, 0.52, 0.59),
            material=PhongMaterial(shininess=20.0),
        )
        platform_top.position = np.array([0.0, 0.235, 0.0], dtype=np.float32)
        scene.add(platform_top)

        for x_position in (-1.75, 1.75):
            support = Box(
                dimensions=(0.18, 1.25, 0.18),
                color=(0.72, 0.73, 0.70),
                material=PhongMaterial(
                    specular_color=(0.48, 0.48, 0.48),
                    shininess=48.0,
                ),
            )
            support.position = np.array(
                [x_position, 0.88, 0.0],
                dtype=np.float32,
            )
            scene.add(support)

        control_stand = Box(
            dimensions=(1.2, 1.1, 0.8),
            color=(0.20, 0.25, 0.32),
            material=LambertMaterial(),
        )
        control_stand.position = np.array([-4.4, 0.35, 1.8], dtype=np.float32)
        scene.add(control_stand)

        control_screen = Box(
            dimensions=(1.05, 0.62, 0.08),
            color=(0.10, 0.58, 0.73),
            material=PhongMaterial(
                specular_color=(0.35, 0.65, 0.72),
                shininess=64.0,
            ),
        )
        control_screen.position = np.array([-4.4, 1.1, 1.39], dtype=np.float32)
        control_screen.rotation[0] = -0.18
        scene.add(control_screen)

        for index, indicator_color in enumerate(
            ((0.15, 0.85, 0.35), (0.95, 0.72, 0.12), (0.9, 0.18, 0.12))
        ):
            indicator = Sphere(
                radius=0.09,
                segments=12,
                rings=8,
                color=indicator_color,
                material=PhongMaterial(
                    specular_color=(0.5, 0.5, 0.5),
                    shininess=40.0,
                ),
            )
            indicator.position = np.array(
                [-4.72 + index * 0.3, 0.76, 1.35],
                dtype=np.float32,
            )
            scene.add(indicator)

        for x_position in (-1.7, 1.7):
            for z_position in (-1.7, 1.7):
                pad_marker = Box(
                    dimensions=(0.12, 0.03, 0.12),
                    color=(0.95, 0.58, 0.12),
                )
                pad_marker.position = np.array(
                    [x_position, 0.31, z_position],
                    dtype=np.float32,
                )
                scene.add(pad_marker)

        rocket = Rocket()
        rocket.position = np.array([0.0, 0.30, 0.0], dtype=np.float32)
        scene.add(rocket)

        movement_rig = MovementRig(move_speed=4.0, turn_speed=1.5)
        movement_rig.position = np.array([0.0, 3.2, 10.5], dtype=np.float32)
        movement_rig.rotation[0] = -0.23
        camera = Camera(field_of_view=0.82, near=0.1, far=100.0)
        movement_rig.add(camera)

        clock = pygame.time.Clock()
        running = True
        paused = False
        print(
            "Cenario lunar: WASD move; Q/E desce/sobe; setas giram; "
            "1/2 articulam suportes; 3/4 ajustam chama; "
            "P pausa; ESC fecha."
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
                    elif event.key == pygame.K_1:
                        rocket.adjust_support_angle(-0.1)
                    elif event.key == pygame.K_2:
                        rocket.adjust_support_angle(0.1)
                    elif event.key == pygame.K_3:
                        rocket.adjust_flame_scale(-0.1)
                    elif event.key == pygame.K_4:
                        rocket.adjust_flame_scale(0.1)
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
