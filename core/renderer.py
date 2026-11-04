from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_TEXTURE0,
    GL_TEXTURE_2D,
    GL_TRIANGLES,
    glActiveTexture,
    glBindTexture,
    glClear,
    glClearColor,
    glDeleteProgram,
    glDisableVertexAttribArray,
    glDrawArrays,
    glEnable,
    glGetAttribLocation,
    glGetUniformLocation,
    glUseProgram,
    glViewport,
)

from core.opengl_utils import OpenGLUtils
from core.uniform import Uniform


class Renderer:
    VERTEX_SHADER = """
        #version 120
        attribute vec3 a_position;
        attribute vec2 a_uv;
        uniform mat4 u_model;
        uniform mat4 u_view;
        uniform mat4 u_projection;
        varying vec2 v_uv;

        void main() {
            v_uv = a_uv;
            gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
        }
    """

    FRAGMENT_SHADER = """
        #version 120
        uniform vec3 u_color;
        uniform sampler2D u_texture;
        uniform int u_use_texture;
        varying vec2 v_uv;

        void main() {
            vec4 surface_color = vec4(u_color, 1.0);
            if (u_use_texture == 1) {
                surface_color = texture2D(u_texture, v_uv);
            }
            gl_FragColor = surface_color;
        }
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.program = OpenGLUtils.create_program(
            self.VERTEX_SHADER,
            self.FRAGMENT_SHADER,
        )
        self.position_location = glGetAttribLocation(self.program, "a_position")
        self.uv_location = glGetAttribLocation(self.program, "a_uv")
        self.model_uniform = Uniform(
            "u_model",
            glGetUniformLocation(self.program, "u_model"),
        )
        self.view_uniform = Uniform(
            "u_view",
            glGetUniformLocation(self.program, "u_view"),
        )
        self.projection_uniform = Uniform(
            "u_projection",
            glGetUniformLocation(self.program, "u_projection"),
        )
        self.color_uniform = Uniform(
            "u_color",
            glGetUniformLocation(self.program, "u_color"),
        )
        self.texture_uniform = Uniform(
            "u_texture",
            glGetUniformLocation(self.program, "u_texture"),
        )
        self.use_texture_uniform = Uniform(
            "u_use_texture",
            glGetUniformLocation(self.program, "u_use_texture"),
        )
        self.resize(width, height)

        glEnable(GL_DEPTH_TEST)
        glUseProgram(self.program)
        self.texture_uniform.set_int(0)

    def resize(self, width: int, height: int) -> None:
        self.width = max(width, 1)
        self.height = max(height, 1)
        glViewport(0, 0, self.width, self.height)

    def render(self, scene, camera) -> None:
        glClearColor(*scene.background, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)
        aspect_ratio = self.width / self.height
        self.view_uniform.set_matrix4(camera.view_matrix())
        self.projection_uniform.set_matrix4(camera.projection_matrix(aspect_ratio))

        for obj, world_matrix in scene.iter_objects():
            position_attribute = obj.attributes.get("a_position")
            if position_attribute is None:
                continue

            position_attribute.bind(self.position_location)
            uv_attribute = obj.attributes.get("a_uv")
            if uv_attribute is not None:
                uv_attribute.bind(self.uv_location)
            self.use_texture_uniform.set_int(int(obj.texture is not None))
            if obj.texture is not None:
                glActiveTexture(GL_TEXTURE0)
                obj.texture.bind()

            self.model_uniform.set_matrix4(world_matrix)
            self.color_uniform.set_vector3(obj.color)
            glDrawArrays(GL_TRIANGLES, 0, position_attribute.vertex_count)
            glDisableVertexAttribArray(self.position_location)
            if uv_attribute is not None:
                glDisableVertexAttribArray(self.uv_location)
            if obj.texture is not None:
                glBindTexture(GL_TEXTURE_2D, 0)

    def dispose(self) -> None:
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0
