"""ARES — Operação Horizonte. Run with .venv/Scripts/python main.py."""
import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
import pygame
from OpenGL import GL
from PIL import Image

from animation.mission import Mission
from camera import Camera, MovementRig
from core import Renderer
from core.hud import HUD
from environment.mars import build_scene

ROOT = Path(__file__).resolve().parent


def aim(rig, eye, target):
    eye, target = np.array(eye, np.float32), np.array(target, np.float32)
    direction = target - eye
    rig.position = eye
    rig.rotation[:] = (math.atan2(float(direction[1]), float(np.linalg.norm(direction[[0,2]]))),
                       math.atan2(float(-direction[0]), float(-direction[2])), 0)


def capture(path, width, height):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
    pixels = GL.glReadPixels(0,0,width,height,GL.GL_RGB,GL.GL_UNSIGNED_BYTE)
    Image.frombytes("RGB",(width,height),pixels).transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(path)
    print(f"Captura: {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify",action="store_true",help="Renderiza fases da missão, salva evidências e encerra.")
    parser.add_argument("--time",type=float,default=0,help="Inicia neste segundo da missão.")
    parser.add_argument("--frames",type=int,default=0,help="Encerra após N quadros (diagnóstico).")
    parser.add_argument("--hidden",action="store_true",help="Janela oculta para verificação automatizada.")
    parser.add_argument("--view",choices=("1","2","3"),default="1",help="Vista inicial: geral, rover ou base.")
    args = parser.parse_args(argv)
    pygame.init()
    renderer = scene = hud = None
    try:
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,1)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER,1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE,24)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS,1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES,4)
        width,height = 1440,900
        flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        if args.hidden:
            flags |= pygame.HIDDEN
        try:
            pygame.display.set_mode((width,height),flags)
        except pygame.error:
            # Keep the application usable on drivers without multisampling.
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS,0)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES,0)
            pygame.display.set_mode((width,height),flags)
        pygame.display.set_caption("ARES — Operação Horizonte | Taagny Augusto e Gustavo Aliani")
        print("GPU:",GL.glGetString(GL.GL_RENDERER).decode())
        print("OpenGL:",GL.glGetString(GL.GL_VERSION).decode())
        renderer = Renderer(width,height)
        scene,rover,drone = build_scene()
        mission = Mission(rover,drone)
        mission.update(args.time)
        hud = HUD()
        rig = MovementRig(move_speed=6,turn_speed=1.1)
        camera = Camera(field_of_view=.78,far=160)
        rig.add(camera)
        aim(rig,(12,7.5,17),(-.6,1,-2.0))
        clock = pygame.time.Clock()
        paused,orbital,running = False,False,True
        camera_name = "geral"
        if args.view == "2":
            camera_name = "rover"; aim(rig,(-10,4.5,-7),(-3.2,1.3,0))
        elif args.view == "3":
            camera_name = "base"; aim(rig,(11,5,6),(2.3,1,-4))
        frames = 0
        view_time = 0.0
        started = time.perf_counter()
        checks = iter(((0,"1",True,False),(6,"1",True,False),(10.5,"1",True,False),
                       (16,"1",True,False),(21,"1",True,False),(26,"1",True,False),
                       (31.5,"1",True,False),(34,"1",True,False),
                       (16,"2",True,False),(16,"3",True,False),
                       (16,"1",False,False),(16,"1",True,True)))
        while running:
            dt = min(clock.tick(60)/1000,.1)
            save = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.WINDOWSIZECHANGED:
                    width,height = pygame.display.get_window_size()
                    renderer.resize(width,height)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = hud.click(event.pos)
                    if action == "pause": paused = not paused
                    elif action == "restart": mission.reset(); paused = False
                    elif action == "help": hud.help = not hud.help
                    hud.last_update = -1000
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    elif event.key in (pygame.K_p,pygame.K_SPACE): paused = not paused
                    elif event.key == pygame.K_r: mission.reset(); paused = False
                    elif event.key == pygame.K_h: hud.help = not hud.help
                    elif event.key == pygame.K_l: renderer.shadows_enabled = not renderer.shadows_enabled
                    elif event.key == pygame.K_c: orbital = not orbital; camera_name = "orbital" if orbital else "livre"
                    elif event.key == pygame.K_1:
                        orbital = False; camera_name = "geral"; aim(rig,(12,7.5,17),(-.6,1,-2.0))
                    elif event.key == pygame.K_2:
                        orbital = False; camera_name = "rover"; aim(rig,(-10,4.5,-7),(-3.2,1.3,0))
                    elif event.key == pygame.K_3:
                        orbital = False; camera_name = "base"; aim(rig,(11,5,6),(2.3,1,-4))
                    elif event.key == pygame.K_F12:
                        save = ROOT/"artifacts"/f"ares-{pygame.time.get_ticks()}.png"
                    hud.last_update = -1000
            keys = pygame.key.get_pressed()
            if any(keys[k] for k in (pygame.K_w,pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_q,pygame.K_e,
                                     pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT)):
                orbital = False; camera_name = "livre"
            if args.verify:
                try:
                    sample,view,shadows,help_open = next(checks)
                except StopIteration:
                    break
                mission.reset(); mission.update(sample)
                paused = True
                renderer.shadows_enabled = shadows
                hud.help = help_open
                if view == "1": aim(rig,(12,7.5,17),(-.6,1,-2)); camera_name = "geral"
                elif view == "2": aim(rig,(-10,4.5,-7),(-3.2,1.3,0)); camera_name = "rover"
                elif view == "3": aim(rig,(11,5,6),(2.3,1,-4)); camera_name = "base"
                suffix = "-sem-sombras" if not shadows else ("-ajuda" if help_open else "")
                save = ROOT/"artifacts"/f"verify-{sample:04.1f}-cam{view}{suffix}.png"
                hud.last_update = -1000
            else:
                mission.update(0 if paused else dt)
            view_time += dt
            if orbital:
                a = .55 + view_time*.09
                aim(rig,(23*math.sin(a),10,23*math.cos(a)),(-.5,1,-2))
            rig.move_speed = 12 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 6
            rig.update(dt,keys)
            scene.mission_time = mission.time
            scene.scanning = mission.index == 3
            renderer.render(scene,camera)
            hud.draw(width,height,mission,paused,clock.get_fps(),camera_name)
            if save:
                capture(save,width,height)
            error = GL.glGetError()
            if error != GL.GL_NO_ERROR:
                raise RuntimeError(f"Erro OpenGL: {error}")
            pygame.display.flip()
            frames += 1
            if args.frames and frames>=args.frames:
                break
        elapsed = time.perf_counter()-started
        print(f"OK: {frames} quadros; {frames/max(elapsed,.001):.1f} FPS médios; "
              f"missão {mission.time:.1f}s; {mission.label}.")
        return 0
    except Exception as error:
        import traceback
        traceback.print_exc()
        print(f"Não foi possível executar ARES: {error}",file=sys.stderr)
        return 1
    finally:
        if hud is not None: hud.dispose()
        if scene is not None: scene.dispose()
        if renderer is not None: renderer.dispose()
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
