import glfw
from OpenGL.GL import *
import numpy as np
import math

def main():
    # Инициализация GLFW
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Создание окна
    window = glfw.create_window(800, 600, "pup", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    # Вершинный шейдер
    vertex_shader = """
    #version 330 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aColor;
    out vec3 fragColor;
    uniform mat4 model;
    void main() {
        gl_Position = model * vec4(aPos, 1.0);
        fragColor = aColor;
    }
    """

    # Фрагментный шейдер
    fragment_shader = """
    #version 330 core
    in vec3 fragColor;
    out vec4 FragColor;
    void main() {
        FragColor = vec4(fragColor, 1.0);
    }
    """

    # Компиляция шейдеров
    shader = compile_shader(vertex_shader, fragment_shader)

    # Вершины треугольника (позиция + цвет)
    vertices = np.array([
        # x    y     z    r    g    b
        0.0,  0.5,  0.0, 0.0, 0.0, 0.0,  # вершина сверху
        -0.5, -0.5, 0.0, 0.0, 0.0, 0.0,  # левая
        0.5, -0.5, 0.0, 0.0, 0.0, 0.0,  # правая
    ], dtype=np.float32)

    # VBO и VAO
    vbo = glGenBuffers(1)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Атрибуты вершин
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    glUseProgram(shader)

    # Основной цикл
    while not glfw.window_should_close(window):
        glClearColor(0.5, 0.5, 0.5, 1.0)  # Серый фон (#888)
        glClear(GL_COLOR_BUFFER_BIT)

        # Здесь будет логика рендеринга (зависит от задачи)

        # Модельная матрица (без преобразований)
        model = np.identity(4, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)

        # Рисуем треугольник
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        #-------------------------------

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

def compile_shader(vertex_source, fragment_source):
    # Компиляция вершинного шейдера
    vertex = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex, vertex_source)
    glCompileShader(vertex)
    if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(vertex))
        raise RuntimeError("Vertex shader compilation failed")

    # Компиляция фрагментного шейдера
    fragment = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment, fragment_source)
    glCompileShader(fragment)
    if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(fragment))
        raise RuntimeError("Fragment shader compilation failed")

    # Создание программы
    program = glCreateProgram()
    glAttachShader(program, vertex)
    glAttachShader(program, fragment)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print(glGetProgramInfoLog(program))
        raise RuntimeError("Shader program linking failed")

    glDeleteShader(vertex)
    glDeleteShader(fragment)
    return program

if __name__ == "__main__":
    main()
