# Cena 3D: foguete e astronauta

Projeto acadêmico de computação gráfica: uma cena 3D interativa de lançamento
espacial, feita em Python, Pygame e OpenGL. Os modelos são montados com
primitivas geométricas e hierarquias de objetos; a sequência de lançamento é
controlada por uma máquina de estados.

## Integrantes

Preencha com os nomes completos e, se necessário, as matrículas:

- Taagny Augusto 
- Gustavo Aliani

## Temas do trabalho

- Transformações geométricas e composição hierárquica de objetos 3D.
- Geometrias poligonais, coordenadas UV e texturas procedurais.
- Câmera em perspectiva e controles de navegação.
- Iluminação direcional e modelos de reflexão Lambert e Phong.
- Shaders GLSL, atributos de vértice e uniforms.
- Shadow mapping com framebuffer de profundidade.
- Animação baseada em delta time e máquina de estados.

## Descrição da cena e da interação

A cena representa uma plataforma de lançamento em terreno lunar. Ela contém
um foguete composto por corpo, ogiva, janela, aletas, suportes articulados e
chama, além de um astronauta com capacete, visor, mochila, braços e pernas.
O solo e a chama recebem texturas geradas pelo próprio programa; não são
necessários arquivos de imagem externos.

Ao iniciar, a sequência passa automaticamente por espera, contagem regressiva,
decolagem e aceno do astronauta. Depois de aproximadamente 15 segundos, a
animação chega ao estado concluído e permanece nele. **P** pausa ou retoma a
animação sem interromper a renderização ou os controles da câmera; **R** volta
ao início e retoma a animação.

## Instalação e execução

Requisitos: Python 3.10 ou superior, placa/driver com suporte a OpenGL e
Windows, Linux ou macOS com ambiente gráfico. No Windows, abra o terminal na
pasta do projeto e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Se o comando `py` não estiver disponível, use `python` para criar o ambiente:

```powershell
python -m venv .venv
```

O Pygame cria a janela e o contexto OpenGL. O renderer utiliza shaders GLSL
compatíveis com OpenGL 2.1. As dependências Python estão listadas em
`requirements.txt`.

## Controles

| Tecla | Ação |
|---|---|
| W / S | Avançar / recuar a câmera |
| A / D | Mover a câmera para a esquerda / direita |
| Q / E | Descer / subir a câmera |
| Setas esquerda / direita | Girar a câmera horizontalmente |
| Setas cima / baixo | Inclinar a câmera verticalmente |
| P | Pausar / retomar a animação |
| R | Reiniciar a sequência e retomar a animação |
| Esc | Fechar a janela |

O movimento da câmera continua disponível enquanto a animação está pausada.

## Contribuições individuais

Preencha esta seção de acordo com o trabalho efetivamente realizado por cada
pessoa:

| Integrante | Contribuições |
|---|---|
| [Nome do integrante 1] | [Descrever tarefas e arquivos desenvolvidos] |
| [Nome do integrante 2] | [Descrever tarefas e arquivos desenvolvidos] |
| [Nome do integrante 3] | [Descrever tarefas e arquivos desenvolvidos] |

## Fontes e créditos

- As texturas do terreno e da chama são procedurais e geradas em
  `environment/terrain.py`; não utilizam imagens de terceiros.
- Pygame-ce: <https://pyga.me/docs/>
- PyOpenGL: <https://pyopengl.sourceforge.net/>
- NumPy: <https://numpy.org/doc/>
- Pillow: <https://pillow.readthedocs.io/>
- OpenGL e GLSL: <https://www.khronos.org/opengl/>

## Recursos gráficos: arquivos, classes e funções

| Recurso | Arquivos e implementação |
|---|---|
| Aplicação, janela e loop | `main.py`, função `main()` |
| Grafo de cena e transformações hierárquicas | `core/object3d.py`, classe `Object3D`; `core/scene.py`, classe `Scene`; `core/matrix.py`, classe `Matrix` |
| Renderer, shaders de iluminação e shadow mapping | `core/renderer.py`, classe `Renderer` |
| Framebuffer e textura de profundidade | `core/shadow_map.py`, classe `ShadowMap` |
| Buffers de atributos e uniforms GLSL | `core/attribute.py`, classe `Attribute`; `core/uniform.py`, classe `Uniform` |
| Luz direcional | `core/light.py`, classe `DirectionalLight` |
| Câmera em perspectiva e navegação | `camera/camera.py`, classe `Camera`; `camera/movement_rig.py`, classe `MovementRig` |
| Primitivas | `geometries/box.py` (`Box`), `geometries/cylinder.py` (`Cylinder`), `geometries/sphere.py` (`Sphere`), `geometries/cone.py` (`Cone`) e `geometries/plane.py` (`Plane`) |
| Materiais Lambert e Phong | `materials/lambert.py` (`LambertMaterial`) e `materials/phong.py` (`PhongMaterial`) |
| Texturas procedurais | `environment/terrain.py`, funções `create_lunar_texture()` e `create_flame_texture()` |
| Foguete hierárquico e chama articulada | `models/rocket.py`, classe `Rocket`; métodos `set_support_angle()` e `set_flame_scale()` |
| Astronauta hierárquico e articulações | `models/astronaut.py`, classe `Astronaut`; métodos `set_arm_swing()`, `set_leg_swing()`, `set_raised_arm_angle()`, `set_head_yaw()` e `set_body_yaw()` |
| Sequência de animação | `animation/state_machine.py`, enumeração `AnimationState` e classe `StateMachine`; `reset()` reinicia a sequência e `update()` avança o tempo e os estados |

### Atributos, uniforms e shaders

As malhas enviam ao renderer os atributos `a_position` (posição), `a_uv`
(coordenada de textura, quando disponível) e `a_normal` (normal). O shader de
sombra usa a posição dos vértices para escrever profundidade.

O shader principal utiliza uniforms de transformação (`u_model`, `u_view`,
`u_projection`, `u_normal_matrix` e `u_light_space_matrix`), material e
textura (`u_color`, `u_texture`, `u_use_texture`, `u_material_model`,
`u_specular_color` e `u_shininess`), iluminação e câmera
(`u_light_direction`, `u_light_color`, `u_ambient_strength` e
`u_camera_position`) e sombras (`u_shadow_map` e `u_shadow_texel_size`). A
iluminação ambiente e difusa é combinada com o termo especular para materiais
Phong. A visibilidade da sombra afeta a luz direta, não a componente ambiente.

## Declaração de uso de inteligência artificial

Ferramentas de inteligência artificial foram utilizadas como apoio durante o
desenvolvimento, incluindo sugestões de implementação, análise de erros,
revisão de código e preparação de documentação. O código foi integrado e
testado no projeto. Os integrantes devem revisar o resultado e ajustar esta
declaração para refletir fielmente o uso feito e as regras da disciplina.
