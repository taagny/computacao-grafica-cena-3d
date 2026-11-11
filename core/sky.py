"""Procedural sky gradient and distant stars, evaluated along camera rays."""
import numpy as np
from OpenGL import GL
from core.attribute import Attribute
from core.opengl_utils import OpenGLUtils
from core.uniform import Uniform


class Sky:
    VERTEX = """#version 120
    attribute vec2 a_position;
    varying vec2 uv;
    void main(){ uv = a_position; gl_Position = vec4(a_position,1.0,1.0); }
    """
    FRAGMENT = """#version 120
    varying vec2 uv;
    uniform vec3 u_right;
    uniform vec3 u_up;
    uniform vec3 u_forward;
    uniform vec2 u_projection;
    float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
    void main(){
        vec3 ray = normalize(u_forward + u_right*uv.x*u_projection.x + u_up*uv.y*u_projection.y);
        float height = max(ray.y,0.0);
        vec3 horizon = vec3(0.32,0.205,0.20);
        vec3 zenith = vec3(0.035,0.055,0.10);
        vec3 color = mix(horizon,zenith,smoothstep(0.0,0.65,height));
        float sun = max(dot(ray,normalize(vec3(-0.8,1.0,-0.45))),0.0);
        color += vec3(0.22,0.09,0.025)*pow(sun,12.0);
        vec2 stars = vec2(atan(ray.z,ray.x),asin(ray.y))*210.0;
        vec2 cell = floor(stars);
        float star = (1.0-smoothstep(0.03,0.12,length(fract(stars)-0.5)))*step(0.985,hash(cell));
        color += vec3(star*smoothstep(0.14,0.5,height)*0.5);
        gl_FragColor=vec4(color,1.0);
    }
    """

    def __init__(self):
        self.program = OpenGLUtils.create_program(self.VERTEX,self.FRAGMENT)
        self.quad = Attribute("a_position",np.array([[-1,-1],[1,-1],[1,1],[-1,-1],[1,1],[-1,1]],np.float32),2)
        self.location = GL.glGetAttribLocation(self.program,"a_position")
        self.uniforms = {name:Uniform(name,GL.glGetUniformLocation(self.program,name))
                         for name in ("u_right","u_up","u_forward","u_projection")}

    def render(self,camera,aspect):
        world = np.linalg.inv(camera.view_matrix())
        GL.glUseProgram(self.program)
        GL.glDisable(GL.GL_DEPTH_TEST)
        self.uniforms["u_right"].set_vector3(world[:3,0])
        self.uniforms["u_up"].set_vector3(world[:3,1])
        self.uniforms["u_forward"].set_vector3(-world[:3,2])
        tangent = np.tan(camera.field_of_view/2)
        self.uniforms["u_projection"].set_vector2((aspect*tangent,tangent))
        self.quad.bind(self.location)
        GL.glDrawArrays(GL.GL_TRIANGLES,0,6)
        GL.glDisableVertexAttribArray(self.location)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def dispose(self):
        self.quad.dispose()
        GL.glDeleteProgram(self.program)
