"""Pygame typography composited over OpenGL by a transparent GLSL quad."""
import ctypes
import numpy as np
import pygame
from OpenGL import GL
from core.opengl_utils import OpenGLUtils


class HUD:
    VERTEX = """#version 120
    attribute vec2 a_position;
    varying vec2 uv;
    void main(){ uv = (a_position + 1.0) * 0.5;
                 gl_Position = vec4(a_position, 0.0, 1.0); }
    """
    FRAGMENT = """#version 120
    uniform sampler2D image;
    varying vec2 uv;
    void main(){ gl_FragColor = texture2D(image, uv); }
    """

    def __init__(self):
        self.program = OpenGLUtils.create_program(self.VERTEX, self.FRAGMENT)
        self.location = GL.glGetAttribLocation(self.program, "a_position")
        self.texture = GL.glGenTextures(1)
        self.buffer = GL.glGenBuffers(1)
        data = np.array([[-1,-1],[1,-1],[1,1],[-1,-1],[1,1],[-1,1]], np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_STATIC_DRAW)
        self.last_update = -1
        self.size = (0, 0)
        self.buttons = {}
        self.fonts = {}
        self.help = False

    def font(self, size, mono=False):
        key = (size, mono)
        if key not in self.fonts:
            family = "consolas" if mono else "bahnschrift, segoeui, arial"
            self.fonts[key] = pygame.font.SysFont(family, size)
        return self.fonts[key]

    def click(self, point):
        return next((name for name, rect in self.buttons.items() if rect.collidepoint(point)), None)

    def draw(self, width, height, mission, paused, fps, camera_name):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100 or self.size != (width, height):
            self._upload(width, height, mission, paused, fps, camera_name)
            self.last_update, self.size = now, (width, height)
        GL.glUseProgram(self.program)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer)
        GL.glEnableVertexAttribArray(self.location)
        GL.glVertexAttribPointer(self.location, 2, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
        GL.glDisableVertexAttribArray(self.location)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glDisable(GL.GL_BLEND)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def _upload(self, width, height, mission, paused, fps, camera_name):
        w, h = 1440, max(720, round(height * 1440 / max(width, 1)))
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        ink, white, muted, cyan, orange = (10,18,26,230), (232,235,226), (148,166,171), (95,216,220), (244,118,65)

        def text(value, x, y, size=18, color=white, mono=False):
            surface.blit(self.font(size, mono).render(value, True, color), (x,y))

        pygame.draw.rect(surface, ink, (0, 0, w, 98))
        pygame.draw.line(surface, (63,77,81), (32, 97), (w-32,97))
        pygame.draw.rect(surface, orange, (32, 25, 5, 47))
        text("ARES", 53, 13, 50)
        text("O P E R A Ç Ã O   H O R I Z O N T E", 221, 28, 19)
        text("PROGRAMA DE EXPLORAÇÃO  /  ESTAÇÃO 04", 222, 56, 13, muted, True)
        pygame.draw.circle(surface, orange if paused else cyan, (1090, 38), 4)
        text("PAUSADO" if paused else "SISTEMAS ONLINE", 1104, 28, 15, cyan, True)
        text(f"SOL 128   /   {fps:04.1f} FPS", 1104, 54, 13, muted, True)
        text("MARS", 36, 121, 16, cyan, True)
        text("04.68° S / 137.44° E", 36, 146, 13, muted, True)
        text("CRATERA GALE · SETOR HORIZONTE", 36, 168, 12, muted, True)
        text("CAM " + camera_name.upper(), w-289, 125, 14, white, True)
        text("1 GERAL   2 ROVER   3 BASE", w-289, 150, 12, muted, True)
        bottom = h - 185
        pygame.draw.rect(surface, ink, (24, bottom, w-48, 161), border_radius=10)
        pygame.draw.rect(surface, (49,67,74), (24, bottom, w-48, 161), 1, border_radius=10)
        text(f"{mission.index+1:02d} / 08   SEQUÊNCIA DA MISSÃO", 46, bottom+15, 12, cyan, True)
        text(mission.label, 45, bottom+36, 26)
        text(mission.description, 46, bottom+75, 16, muted)
        track_x, track_y, track_w = 46, bottom+116, 778
        pygame.draw.rect(surface, (44,58,63), (track_x,track_y,track_w,3))
        pygame.draw.rect(surface, cyan, (track_x,track_y,max(1,round(track_w*mission.progress)),3))
        cumulative = 0
        for _, duration, _ in mission.STAGES[:-1]:
            cumulative += duration
            pygame.draw.circle(surface, muted, (track_x+round(track_w*cumulative/mission.TOTAL),track_y+1),3)
        text(f"T + {mission.time:05.1f}s  /  {mission.TOTAL:.1f}s", 46, bottom+130, 12, muted, True)
        text("PYTHON / OPENGL  ·  SHADOW MAPPING", 490, bottom+130, 12, muted, True)
        pygame.draw.line(surface, (49,67,74), (853,bottom+20), (853,bottom+140))
        text("EXPLORADORES", 878,bottom+17,12,muted,True)
        text("R-01  ROVER",878,bottom+43,17)
        text("D-04  DRONE",878,bottom+76,17)
        text(f"Y {mission.drone.position[1]:.1f} m",1038,bottom+79,13,cyan,True)
        text("ENLACE ESTABELECIDO" if mission.index>=4 else "CANAL DE TELEMETRIA",878,bottom+121,11,cyan,True)
        self.buttons = {}
        for j, (name, label) in enumerate((("pause", "RETOMAR [P]" if paused else "PAUSAR [P]"),
                                         ("restart", "REINICIAR [R]"), ("help", "CONTROLES [H]"))):
            rect = pygame.Rect(1191,bottom+16+j*43,200,34)
            pygame.draw.rect(surface, (30,47,56), rect, border_radius=5)
            text(label,rect.x+15,rect.y+9,12,white,True)
            self.buttons[name] = pygame.Rect(round(rect.x*width/w), round(rect.y*height/h),
                                            round(rect.w*width/w), round(rect.h*height/h))
        text("TAAGNY AUGUSTO + GUSTAVO ALIANI  /  COMPUTAÇÃO GRÁFICA",32,h-18,10,muted,True)
        text("H AJUDA   ·   C CÂMERA ORBITAL   ·   F12 CAPTURA",w-462,h-18,10,muted,True)
        if self.help:
            pygame.draw.rect(surface, (10,18,26,248), (w//2-290,205,580,284), border_radius=12)
            text("CONTROLES DE VOO",w//2-260,226,25)
            for j,line in enumerate(("W A S D   mover câmera    Q / E   altura", "SETAS     orientar       SHIFT   acelerar",
                                      "1 / 2 / 3 vistas         C       órbita automática",
                                      "P / ESPAÇO pausar        R       reiniciar",
                                      "L         sombras        F12     salvar captura",
                                      "H         esta ajuda     ESC     sair")):
                text(line,w//2-260,276+j*29,15,muted,True)
        if surface.get_size() != (width,height):
            surface = pygame.transform.smoothscale(surface, (width,height))
        GL.glBindTexture(GL.GL_TEXTURE_2D,self.texture)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,GL.GL_LINEAR)
        GL.glTexImage2D(GL.GL_TEXTURE_2D,0,GL.GL_RGBA,width,height,0,GL.GL_RGBA,GL.GL_UNSIGNED_BYTE,
                        pygame.image.tobytes(surface,"RGBA",True))
        GL.glBindTexture(GL.GL_TEXTURE_2D,0)

    def dispose(self):
        GL.glDeleteTextures([self.texture])
        GL.glDeleteBuffers(1,[self.buffer])
        GL.glDeleteProgram(self.program)
