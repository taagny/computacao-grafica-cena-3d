import numpy as np
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FRAMEBUFFER,
    GL_TEXTURE0,
    GL_TEXTURE1,
    GL_TEXTURE_2D,
    GL_TRIANGLES,
    glActiveTexture,
    glBindTexture,
    glBindFramebuffer,
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
from core.shadow_map import ShadowMap
from core.uniform import Uniform


class Renderer:
    SHADOW_VERTEX_SHADER = """
        #version 120
        attribute vec3 a_position;
        uniform mat4 u_model;
        uniform mat4 u_light_space_matrix;

        void main() {
            gl_Position = u_light_space_matrix * u_model * vec4(a_position, 1.0);
        }
    """

    SHADOW_FRAGMENT_SHADER = """
        #version 120
        void main() {
        }
    """

    VERTEX_SHADER = """
        #version 120
        attribute vec3 a_position;
        attribute vec2 a_uv;
        attribute vec3 a_normal;
        uniform mat4 u_model;
        uniform mat4 u_view;
        uniform mat4 u_projection;
        uniform mat4 u_light_space_matrix;
        uniform mat4 u_normal_matrix;
        varying vec2 v_uv;
        varying vec3 v_world_position;
        varying vec3 v_world_normal;
        varying vec4 v_light_space_position;

        void main() {
            v_uv = a_uv;
            vec4 world_position = u_model * vec4(a_position, 1.0);
            v_world_position = world_position.xyz;
            v_world_normal = mat3(u_normal_matrix) * a_normal;
            v_light_space_position = u_light_space_matrix * world_position;
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
        uniform sampler2D u_shadow_map;
        uniform vec2 u_shadow_texel_size;
        varying vec2 v_uv;
        varying vec3 v_world_position;
        varying vec3 v_world_normal;
        varying vec4 v_light_space_position;

        float shadow_visibility(vec3 normal, vec3 light_direction) {
            vec3 projected = v_light_space_position.xyz / v_light_space_position.w;
            projected = projected * 0.5 + 0.5;
            if (projected.z > 1.0
                || projected.x < 0.0 || projected.x > 1.0
                || projected.y < 0.0 || projected.y > 1.0) {
                return 1.0;
            }

            float bias = max(0.0015 * (1.0 - dot(normal, light_direction)), 0.0004);
            float visibility = 0.0;
            for (int x = -1; x <= 1; x++) {
                for (int y = -1; y <= 1; y++) {
                    float closest_depth = texture2D(
                        u_shadow_map,
                        projected.xy + vec2(float(x), float(y)) * u_shadow_texel_size
                    ).r;
                    visibility += projected.z - bias <= closest_depth ? 1.0 : 0.0;
                }
            }
            return visibility / 9.0;
        }

        void main() {
            vec4 surface_color = vec4(u_color, 1.0);
            if (u_use_texture == 1) {
                surface_color = texture2D(u_texture, v_uv) * vec4(u_color, 1.0);
            }

            vec3 normal = normalize(v_world_normal);
            vec3 light_direction = normalize(-u_light_direction);
            float diffuse_strength = max(dot(normal, light_direction), 0.0);
            float visibility = shadow_visibility(normal, light_direction);
            vec3 direct_lighting = u_light_color * diffuse_strength;

            if (u_material_model == 1 && diffuse_strength > 0.0) {
                vec3 view_direction = normalize(u_camera_position - v_world_position);
                vec3 reflected_direction = reflect(-light_direction, normal);
                float specular_strength = pow(
                    max(dot(view_direction, reflected_direction), 0.0),
                    u_shininess
                );
                direct_lighting += u_specular_color * specular_strength;
            }

            vec3 lighting = vec3(u_ambient_strength) + direct_lighting * visibility;
            gl_FragColor = vec4(surface_color.rgb * lighting, surface_color.a);
        }
    """

    def __init__(self, width: int, height: int, shadow_resolution: int = 2048) -> None:
        self.width = width
        self.height = height
        self.program = OpenGLUtils.create_program(
            self.VERTEX_SHADER,
            self.FRAGMENT_SHADER,
        )
        self.shadow_program = OpenGLUtils.create_program(
            self.SHADOW_VERTEX_SHADER,
            self.SHADOW_FRAGMENT_SHADER,
        )
        self.shadow_map = ShadowMap(shadow_resolution)
        self.position_location = glGetAttribLocation(self.program, "a_position")
        self.uv_location = glGetAttribLocation(self.program, "a_uv")
        self.normal_location = glGetAttribLocation(self.program, "a_normal")
        self.shadow_position_location = glGetAttribLocation(
            self.shadow_program,
            "a_position",
        )
        self.model_uniform = Uniform(
            "u_model",
            glGetUniformLocation(self.program, "u_model"),
        )
        self.light_space_uniform = Uniform(
            "u_light_space_matrix",
            glGetUniformLocation(self.program, "u_light_space_matrix"),
        )
        self.shadow_model_uniform = Uniform(
            "u_model",
            glGetUniformLocation(self.shadow_program, "u_model"),
        )
        self.shadow_light_space_uniform = Uniform(
            "u_light_space_matrix",
            glGetUniformLocation(self.shadow_program, "u_light_space_matrix"),
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
        self.shadow_map_uniform = Uniform(
            "u_shadow_map",
            glGetUniformLocation(self.program, "u_shadow_map"),
        )
        self.shadow_texel_size_uniform = Uniform(
            "u_shadow_texel_size",
            glGetUniformLocation(self.program, "u_shadow_texel_size"),
        )
        self.resize(width, height)

        glEnable(GL_DEPTH_TEST)
        glUseProgram(self.program)
        self.texture_uniform.set_int(0)
        self.shadow_map_uniform.set_int(1)

    def resize(self, width: int, height: int) -> None:
        self.width = max(width, 1)
        self.height = max(height, 1)
        glViewport(0, 0, self.width, self.height)

    def _light_space_matrix(self, light) -> np.ndarray:
        direction = np.asarray(light.direction, dtype=np.float32)
        target = np.asarray([0.0, 2.0, 0.0], dtype=np.float32)
        eye = target - direction * 30.0
        light_view = Matrix.look_at(
            eye,
            target,
            np.asarray([0.0, 1.0, 0.0], dtype=np.float32),
        )
        light_projection = Matrix.orthographic(
            -16.0,
            16.0,
            -14.0,
            14.0,
            0.1,
            70.0,
        )
        return light_projection @ light_view

    def _render_shadow_depth(self, scene, light_space_matrix: np.ndarray) -> None:
        self.shadow_map.bind()
        glViewport(
            0,
            0,
            self.shadow_map.resolution,
            self.shadow_map.resolution,
        )
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shadow_program)
        self.shadow_light_space_uniform.set_matrix4(light_space_matrix)

        for obj, world_matrix in scene.iter_objects():
            position_attribute = obj.attributes.get("a_position")
            if position_attribute is None:
                continue
            position_attribute.bind(self.shadow_position_location)
            self.shadow_model_uniform.set_matrix4(world_matrix)
            glDrawArrays(GL_TRIANGLES, 0, position_attribute.vertex_count)
            glDisableVertexAttribArray(self.shadow_position_location)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.resize(self.width, self.height)

    def render(self, scene, camera) -> None:
        light_space_matrix = self._light_space_matrix(scene.directional_light)
        self._render_shadow_depth(scene, light_space_matrix)
        glClearColor(*scene.background, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)
        self.light_space_uniform.set_matrix4(light_space_matrix)
        self.shadow_texel_size_uniform.set_vector2(
            (
                1.0 / self.shadow_map.resolution,
                1.0 / self.shadow_map.resolution,
            )
        )
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.shadow_map.depth_texture)
        glActiveTexture(GL_TEXTURE0)
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

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, 0)
        glActiveTexture(GL_TEXTURE0)

    def dispose(self) -> None:
        if self.shadow_map is not None:
            self.shadow_map.dispose()
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0
        if self.shadow_program:
            glDeleteProgram(self.shadow_program)
            self.shadow_program = 0
