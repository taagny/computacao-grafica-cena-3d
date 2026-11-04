import sys

import numpy as np
import pygame

from core import Object3D, Renderer, Scene
from core.attribute import Attribute


class RotatingCube(Object3D):
    def __init__(
        self,
        attributes: dict[str, Attribute] | None = None,
        color: tuple[float, float, float] = (0.18, 0.62, 0.95),
    ) -> None:
        super().__init__(attributes=attributes, color=color)
        self.rotation_velocity = np.array([0.55, 0.85, 0.25], dtype=np.float32)

    def update(self, delta_time: float) -> None:
        self.rotation += self.rotation_velocity * delta_time
        super().update(delta_time)


def create_cube_vertices() -> np.ndarray:
    faces = [
        [(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)],
        [(0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)],
        [(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)],
        [(0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)],
        [(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)],
        [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)],
    ]
    triangle_corners = (0, 1, 2, 0, 2, 3)
    vertices = [face[corner] for face in faces for corner in triangle_corners]
    return np.asarray(vertices, dtype=np.float32)


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
        pygame.display.set_caption("Cena 3D - Etapa 1 | P: pausar/retomar")

        renderer = Renderer(width, height)
        scene = Scene(background=(0.035, 0.055, 0.12))
        cube = RotatingCube(
            attributes={
                "a_position": Attribute(
                    "a_position",
                    create_cube_vertices(),
                    component_count=3,
                )
            },
            color=(0.18, 0.62, 0.95),
        )
        cube.rotation = np.array([0.38, 0.25, 0.0], dtype=np.float32)
        scene.add(cube)

        clock = pygame.time.Clock()
        running = True
        paused = False
        print("Controles: P pausa/retoma a animacao; ESC fecha a janela.")

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
            renderer.render(scene)
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
