import numpy as np


def create_lunar_texture(size: int = 256, seed: int = 17) -> np.ndarray:
    if size < 32:
        raise ValueError("A textura precisa ter pelo menos 32 pixels por lado.")

    rng = np.random.default_rng(seed)
    coordinates = np.arange(size, dtype=np.float32) / size
    u, v = np.meshgrid(coordinates, coordinates)

    noise = np.zeros((size, size), dtype=np.float32)
    for frequency, amplitude in ((3, 0.38), (7, 0.24), (15, 0.16), (31, 0.10)):
        phase_u, phase_v = rng.uniform(0.0, 2.0 * np.pi, size=2)
        noise += amplitude * np.sin(
            2.0 * np.pi * (frequency * u + phase_u / (2.0 * np.pi))
        ) * np.cos(
            2.0 * np.pi * (frequency * v + phase_v / (2.0 * np.pi))
        )

    height_map = noise.copy()
    for _ in range(22):
        center_u, center_v = rng.random(2)
        radius = rng.uniform(0.018, 0.075)
        distance_u = np.abs(u - center_u)
        distance_v = np.abs(v - center_v)
        distance_u = np.minimum(distance_u, 1.0 - distance_u)
        distance_v = np.minimum(distance_v, 1.0 - distance_v)
        distance = np.sqrt(distance_u**2 + distance_v**2) / radius
        bowl = np.clip(1.0 - distance**2, 0.0, 1.0)
        rim = np.exp(-((distance - 0.9) / 0.16) ** 2)
        height_map -= 0.34 * bowl
        height_map += 0.13 * rim

    height_map = np.clip(height_map, -0.8, 0.8)
    brightness = (height_map + 0.8) / 1.6

    image = np.empty((size, size, 3), dtype=np.uint8)
    image[:, :, 0] = np.clip(76 + brightness * 65, 0, 255).astype(np.uint8)
    image[:, :, 1] = np.clip(70 + brightness * 59, 0, 255).astype(np.uint8)
    image[:, :, 2] = np.clip(62 + brightness * 51, 0, 255).astype(np.uint8)
    return image


def create_flame_texture(
    width: int = 128,
    height: int = 256,
    seed: int = 29,
) -> np.ndarray:
    if width < 16 or height < 16:
        raise ValueError("A textura da chama precisa ter ao menos 16 pixels por lado.")

    rng = np.random.default_rng(seed)
    u = np.linspace(0.0, 1.0, width, endpoint=False, dtype=np.float32)[None, :]
    v = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    turbulence = np.zeros((height, width), dtype=np.float32)
    for frequency, amplitude in ((4.0, 0.13), (9.0, 0.07), (19.0, 0.035)):
        phase = rng.uniform(0.0, 2.0 * np.pi)
        turbulence += amplitude * np.sin(
            2.0 * np.pi * (frequency * u + 1.7 * v) + phase
        )

    flame_height = np.clip(v + turbulence, 0.0, 1.0)
    edge_fade = np.clip(np.sin(np.pi * u) * 2.6, 0.0, 1.0)
    intensity = np.clip((1.0 - flame_height) * 1.25, 0.0, 1.0) * edge_fade

    image = np.empty((height, width, 3), dtype=np.uint8)
    image[:, :, 0] = np.clip(145.0 + 110.0 * intensity, 0, 255).astype(np.uint8)
    image[:, :, 1] = np.clip(22.0 + 220.0 * intensity**1.5, 0, 255).astype(np.uint8)
    image[:, :, 2] = np.clip(5.0 + 90.0 * intensity**4, 0, 255).astype(np.uint8)
    return image
