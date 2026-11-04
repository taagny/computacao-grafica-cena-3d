from OpenGL.GL import (
    GL_COMPILE_STATUS,
    GL_FRAGMENT_SHADER,
    GL_LINK_STATUS,
    GL_VERTEX_SHADER,
    glAttachShader,
    glCompileShader,
    glCreateProgram,
    glCreateShader,
    glDeleteProgram,
    glDeleteShader,
    glGetProgramInfoLog,
    glGetProgramiv,
    glGetShaderInfoLog,
    glGetShaderiv,
    glLinkProgram,
    glShaderSource,
)


class OpenGLUtils:
    @staticmethod
    def create_program(vertex_source: str, fragment_source: str) -> int:
        vertex_shader = OpenGLUtils._compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = 0
        program = glCreateProgram()

        try:
            fragment_shader = OpenGLUtils._compile_shader(
                fragment_source,
                GL_FRAGMENT_SHADER,
            )
            glAttachShader(program, vertex_shader)
            glAttachShader(program, fragment_shader)
            glLinkProgram(program)

            if not glGetProgramiv(program, GL_LINK_STATUS):
                message = glGetProgramInfoLog(program)
                raise RuntimeError(f"Nao foi possivel vincular os shaders: {message}")

            return program
        except Exception:
            if program:
                glDeleteProgram(program)
            raise
        finally:
            if vertex_shader:
                glDeleteShader(vertex_shader)
            if fragment_shader:
                glDeleteShader(fragment_shader)

    @staticmethod
    def _compile_shader(source: str, shader_type: int) -> int:
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            message = glGetShaderInfoLog(shader)
            glDeleteShader(shader)
            raise RuntimeError(f"Nao foi possivel compilar um shader: {message}")

        return shader
