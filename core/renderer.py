import numpy as np
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

from core.matrix import Matrix
from core.opengl_utils import OpenGLUtils
from core.uniform import Uniform


class Renderer:
    VERTEX_SHADER = """
        #version 120
        attribute vec3 a_position;
        attribute vec2 a_uv;
        attribute vec3 a_normal;
        uniform mat4 u_model;
        uniform mat4 u_view;
        uniform mat4 u_projection;
        uniform mat4 u_normal_matrix;
        varying vec2 v_uv;
        varying vec3 v_world_position;
        varying vec3 v_world_normal;

        void main() {
            v_uv = a_uv;
            vec4 world_position = u_model * vec4(a_position, 1.0);
            v_world_position = world_position.xyz;
            v_world_normal = mat3(u_normal_matrix) * a_normal;
            gl_Position = u_projection * u_view * world_position;
        }
    """

    FRAGMENT_SHADER = """
        #version 120
        uniform vec3 u_color;
        uniform sampler2D u_texture;
        uniform int u_use_texture;
        uniform int u_material_model;
        uniform vec3 u_light_direction;
        uniform vec3 u_light_color;
        uniform vec3 u_camera_position;
        uniform vec3 u_specular_color;
        uniform float u_ambient_strength;
        uniform float u_shininess;
        varying vec2 v_uv;
        varying vec3 v_world_position;
        varying vec3 v_world_normal;

        void main() {
            vec4 surface_color = vec4(u_color, 1.0);
            if (u_use_texture == 1) {
                surface_color = texture2D(u_texture, v_uv) * vec4(u_color, 1.0);
            }

            vec3 normal = normalize(v_world_normal);
            vec3 light_direction = normalize(-u_light_direction);
            float diffuse_strength = max(dot(normal, light_direction), 0.0);
            vec3 lighting = vec3(u_ambient_strength)
                + u_light_color * diffuse_strength;

            if (u_material_model == 1 && diffuse_strength > 0.0) {
                vec3 view_direction = normalize(u_camera_position - v_world_position);
                vec3 reflected_direction = reflect(-light_direction, normal);
                float specular_strength = pow(
                    max(dot(view_direction, reflected_direction), 0.0),
                    u_shininess
                );
                lighting += u_specular_color * specular_strength;
            }

            gl_FragColor = vec4(surface_color.rgb * lighting, surface_color.a);
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
        self.normal_location = glGetAttribLocation(self.program, "a_normal")
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
        self.normal_matrix_uniform = Uniform(
            "u_normal_matrix",
            glGetUniformLocation(self.program, "u_normal_matrix"),
        )
        self.light_direction_uniform = Uniform(
            "u_light_direction",
            glGetUniformLocation(self.program, "u_light_direction"),
        )
        self.light_color_uniform = Uniform(
            "u_light_color",
            glGetUniformLocation(self.program, "u_light_color"),
        )
        self.camera_position_uniform = Uniform(
            "u_camera_position",
            glGetUniformLocation(self.program, "u_camera_position"),
        )
        self.specular_color_uniform = Uniform(
            "u_specular_color",
            glGetUniformLocation(self.program, "u_specular_color"),
        )
        self.ambient_strength_uniform = Uniform(
            "u_ambient_strength",
            glGetUniformLocation(self.program, "u_ambient_strength"),
        )
        self.shininess_uniform = Uniform(
            "u_shininess",
            glGetUniformLocation(self.program, "u_shininess"),
        )
        self.material_model_uniform = Uniform(
            "u_material_model",
            glGetUniformLocation(self.program, "u_material_model"),
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
        view_matrix = camera.view_matrix()
        camera_world_matrix = np.linalg.inv(view_matrix)
        light = scene.directional_light
        self.view_uniform.set_matrix4(view_matrix)
        self.projection_uniform.set_matrix4(camera.projection_matrix(aspect_ratio))
        self.camera_position_uniform.set_vector3(
            (
                float(camera_world_matrix[0, 3]),
                float(camera_world_matrix[1, 3]),
                float(camera_world_matrix[2, 3]),
            )
        )
        self.light_direction_uniform.set_vector3(light.direction)
        self.light_color_uniform.set_vector3(light.color)
        self.ambient_strength_uniform.set_float(light.ambient_strength)

        for obj, world_matrix in scene.iter_objects():
            position_attribute = obj.attributes.get("a_position")
            if position_attribute is None:
                continue

            position_attribute.bind(self.position_location)
            uv_attribute = obj.attributes.get("a_uv")
            if uv_attribute is not None:
                uv_attribute.bind(self.uv_location)
            normal_attribute = obj.attributes.get("a_normal")
            if normal_attribute is None:
                raise ValueError(f"O objeto {obj} nao possui atributo de normais.")
            normal_attribute.bind(self.normal_location)
            self.use_texture_uniform.set_int(int(obj.texture is not None))
            if obj.texture is not None:
                glActiveTexture(GL_TEXTURE0)
                obj.texture.bind()

            self.model_uniform.set_matrix4(world_matrix)
            normal_matrix = Matrix.identity()
            normal_matrix[:3, :3] = np.linalg.inv(
                world_matrix[:3, :3]
            ).T.astype(np.float32)
            self.normal_matrix_uniform.set_matrix4(normal_matrix)
            self.color_uniform.set_vector3(obj.color)
            self.material_model_uniform.set_int(obj.material.model)
            self.specular_color_uniform.set_vector3(obj.material.specular_color)
            self.shininess_uniform.set_float(obj.material.shininess)
            glDrawArrays(GL_TRIANGLES, 0, position_attribute.vertex_count)
            glDisableVertexAttribArray(self.position_location)
            if uv_attribute is not None:
                glDisableVertexAttribArray(self.uv_location)
            glDisableVertexAttribArray(self.normal_location)
            if obj.texture is not None:
                glBindTexture(GL_TEXTURE_2D, 0)

    def dispose(self) -> None:
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0
