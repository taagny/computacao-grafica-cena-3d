"""An original Mars research outpost assembled from framework geometry."""
import math
from pathlib import Path
import numpy as np
from PIL import Image

from core import Scene
from core.light import DirectionalLight
from core.texture import Texture
from core.batching import batch_static
from geometries import Box, Plane
from geometries.base import Geometry
from geometries.torus import Torus
from models.primitives import INK, WHITE, ORANGE, CYAN, box, cylinder, sphere, beam, pivot, place
from models.rover import Rover
from models.drone import Drone

ROOT = Path(__file__).resolve().parents[1]


def image_texture(name):
    with Image.open(ROOT / "assets" / "textures" / name) as image:
        return Texture(np.flipud(np.array(image.convert("RGB"))))


def make_landscape(scene):
    """Batch faceted rocks and distant ridges into one draw call per material."""
    rng = np.random.default_rng(48)
    verts = []
    octa = np.array([(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -0.3, 0)])
    faces = [(1, 0, 3), (1, 3, 2), (1, 2, 4), (1, 4, 0),
             (5, 3, 0), (5, 2, 3), (5, 4, 2), (5, 0, 4)]
    for _ in range(180):
        x, z = rng.uniform(-25, 25, 2)
        if (-5.8 < x < 6.8 and -9 < z < 9):
            continue
        size = rng.uniform(.12, .7)
        points = octa * (size, size * .65, size * 1.4) + (x, .02, z)
        verts.extend(points[list(face)] for face in faces)
    rocks = Geometry(np.array(verts, dtype=np.float32).reshape(-1, 3, 3)[:, ::-1].reshape(-1,3),
                     (0.36, 0.20, 0.145))
    scene.add(rocks)
    # Continuous layered mesas: neighbouring sections share the same ridge.
    verts = []
    count = 72
    angles = np.arange(count) * math.tau / count
    heights = 4.5 + 1.4*np.sin(angles*5) + .8*np.cos(angles*9)
    rings = []
    for radius, factor in ((27,0), (35,1), (41,.95), (49,0)):
        rings.append(np.array([(radius*math.cos(a), -.03+h*factor, radius*math.sin(a))
                               for a,h in zip(angles,heights)]))
    for inner,outer in zip(rings,rings[1:]):
        for i in range(count):
            j = (i+1)%count
            verts.extend((inner[i],outer[i],outer[j],inner[i],outer[j],inner[j]))
    ridge = Geometry(np.array(verts, dtype=np.float32).reshape(-1,3,3)[:,::-1].reshape(-1,3),
                     (.49, .29, .23))
    ridge.cast_shadow = False
    scene.add(ridge)


def build_scene():
    scene = Scene(background=(.32, .205, .20), directional_light=DirectionalLight(
        direction=(-.8, -1, -.45), color=(1.0, .77, .55), ambient_strength=.28))
    floor = Plane(width=100, depth=100, texture=image_texture("martian_regolith.png"),
                  uv_tiles=(24, 24), color=(1, 1, 1))
    floor.cast_shadow = False
    scene.add(floor)
    make_landscape(scene)
    # Inset landing platform, concentric lit rings, target and perimeter bolts.
    cylinder(scene, 2.3, .16, (3.8, .08, 0), INK, segments=64)
    cylinder(scene, 2.08, .035, (3.8, .18, 0), (.28, .33, .34), segments=64)
    for radius in (1.68, 2.14):
        ring = place(scene, Torus(radius=radius, tube=.025, color=CYAN), (3.8, .215, 0), emission=.9)
        ring.cast_shadow = False
    for x in (-.45, .45):
        box(scene, (.12, .012, 1.10), (3.8 + x, .21, 0), WHITE)
    box(scene, (.9, .012, .12), (3.8, .211, 0), WHITE)
    for i in range(8):
        a = i * math.tau / 8
        sphere(scene, .06, (3.8 + 2.15 * math.cos(a), .22, 2.15 * math.sin(a)), ORANGE, emission=.8)
    # Rover corridor, wheel tracks, inspection target and approach beacons.
    for x in (-4.25, -2.15):
        for j in range(45):
            box(scene, (.31, .015, .10), (x, .025, -6 + j * .28), (.34, .18, .12))
    for z in (-6, -3, 0, 3, 6):
        for x in (-5.15, -1.25):
            box(scene, (.10, .02, .55), (x, .028, z), (.83, .62, .37))
    place(scene, Torus(radius=1.82, tube=.018, color=(.96, .57, .22)), (-3.2, .036, 0), emission=.5)
    for x, z in ((-5.6, 2.6), (-5.6, -2.6), (6.6, 2.6), (6.6, -2.6)):
        cylinder(scene, .12, .12, (x, .08, z), INK)
        cylinder(scene, .035, .64, (x, .43, z), WHITE)
        sphere(scene, .09, (x, .8, z), CYAN, emission=1)
    # Modular research habitat, with ribs, inset door, luminous window and sign.
    habitat = pivot(scene, (2.4, 0, -7.3))
    box(habitat, (5.3, .28, 2.9), (0, .18, 0), INK)
    box(habitat, (4.8, 2.1, 2.45), (0, 1.4, 0), (.66, .64, .55))
    box(habitat, (5.1, .23, 2.7), (0, 2.56, 0), WHITE)
    for x in (-2.35, -.85, .85, 2.35):
        box(habitat, (.13, 2.25, 2.60), (x, 1.42, 0), INK)
    box(habitat, (1.08, 1.70, .09), (-1.55, 1.22, 1.29), INK)
    box(habitat, (.83, 1.45, .11), (-1.55, 1.19, 1.35), (.27, .33, .34))
    box(habitat, (.055, 1.35, .02), (-1.91, 1.2, 1.42), CYAN, emission=.9)
    box(habitat, (1.4, .64, .06), (0, 1.68, 1.33), INK)
    box(habitat, (1.18, .44, .07), (0, 1.68, 1.38), (.16, .52, .60), emission=.65)
    box(habitat, (.05, .5, .08), (0, 1.68, 1.43), WHITE)
    for k in range(3):
        box(habitat, (1.1, .12, .38), (-1.55, .10 + k * .1, 2.05 - k * .32), INK)
    sign = Plane(width=2.5, depth=.625, texture=image_texture("station_sign.png"), color=(1, 1, 1))
    place(habitat, sign, (0, 2.94, .05), (-math.pi / 2, 0, 0), emission=.7)
    for x in (-1.32, 1.32):
        beam(habitat, (x, 2.6, 0), (x, 3.3, 0), .025, INK)
    # Dish antenna with concentric discs, mast and receiver.
    antenna = pivot(scene, (6.2, 0, -6.6))
    cylinder(antenna, .32, .18, (0, .10, 0), INK)
    cylinder(antenna, .055, 3.0, (0, 1.5, 0), WHITE)
    dish = pivot(antenna, (0, 3.15, 0))
    dish.rotation[:] = (.5, 0, -.4)
    sphere(dish, .78, (0, 0, 0), WHITE, (1, .15, 1))
    cylinder(dish, .055, .7, (0, .35, 0), ORANGE)
    sphere(dish, .09, (0, .73, 0), CYAN, emission=.9)
    # Two solar arrays: image texture mapped across tilted surfaces.
    for x in (-.5, 3.7):
        solar = pivot(scene, (x, 0, -10.8))
        for offset in (-1.1, 1.1):
            cylinder(solar, .055, 1.1, (offset, .55, 0), INK)
        board = pivot(solar, (0, 1.2, 0))
        board.rotation[0] = .35
        box(board, (3.4, .1, 2.3), (0, 0, 0), WHITE)
        panel = Plane(width=3.22, depth=2.12, color=(1, 1, 1), texture=image_texture("solar_cells.png"))
        place(board, panel, (0, .061, 0))
    for z in (-5.4, -4.6):
        box(scene, (.8, .65, .65), (6.4, .34, z), ORANGE)
        box(scene, (.84, .07, .69), (6.4, .69, z), INK)
    rover, drone = Rover(), Drone()
    for obj, _ in rover.iter_objects():
        obj.scan_surface = True
    scene.add(rover)
    scene.add(drone)
    batch_static(scene, (rover, drone, rover.sensor, drone.gimbal, *rover.wheels, *drone.rotors))
    return scene, rover, drone
