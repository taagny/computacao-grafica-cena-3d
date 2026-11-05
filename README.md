# Cena 3D: foguete e astronauta

Trabalho prático de Computação Gráfica (Ciência da Computação, UNIPAC, 2026/02).
Cena 3D de lançamento espacial feita em Python, Pygame e OpenGL. Os modelos são
montados apenas com primitivas geométricas e hierarquias de objetos, e a
sequência de lançamento é controlada por uma máquina de estados.

## Integrantes e temas

| Integrante |
|---|
| Taagny Augusto |
| Gustavo Aliani |

Temas, escolhidos livremente pela dupla com autorização do professor:

1. **Foguete de brinquedo** (tema 8): foguete em uma plataforma de lançamento, com suportes articulados e subida após uma ação combinada com o segundo elemento.
2. **Astronauta estilizado** (tema 19): astronauta que movimenta braço e cabeça em resposta ao foguete.

## Conteúdos aplicados

- Transformações geométricas (translação, rotação e escala) e composição hierárquica de objetos 3D.
- Geometrias poligonais, coordenadas UV e texturas.
- Câmera em perspectiva e controles de navegação.
- Iluminação direcional e modelos de reflexão Lambert e Phong.
- Shaders GLSL, atributos de vértice e uniforms.
- Shadow mapping com framebuffer de profundidade.
- Animação baseada em delta time e máquina de estados.

## Descrição da cena e da interação

A cena representa uma plataforma de lançamento em terreno lunar, com chão
texturizado, base e topo da plataforma, duas torres de apoio, um painel de
controle com tela e luzes indicadoras, e marcadores no piso. O **foguete** é
composto por corpo, ogiva, motor, janela, três aletas, dois suportes
articulados e chama. O **astronauta** é composto por tronco, painel frontal,
mochila, capacete com visor, dois braços (ombro, braço, cotovelo, antebraço e
mão) e duas pernas (quadril, coxa, joelho, canela e bota).

A sequência é uma máquina de estados em que cada etapa só começa quando a
anterior termina (duração total de cerca de 15 segundos):

| Etapa | Duração | O que acontece |
|---|---|---|
| Aguardando lançamento | 2 s | Foguete e astronauta parados. |
| Contagem regressiva | 4 s | Os dois suportes do foguete giram até cerca de 60° e se afastam do corpo; a chama cresce. |
| Decolagem | 5 s | Só começa depois que os suportes terminam de abrir. O foguete sobe 8 unidades com aceleração suave; a chama aumenta; o astronauta gira a cabeça acompanhando a partida. |
| Astronauta acena | 4 s | Só começa depois que o foguete termina a subida. O astronauta levanta o braço direito, com leve balanço de braço e pernas. |
| Concluída | — | A cena permanece no estado final até a tecla **R**. |

**Interação:** o foguete só decola depois que seus suportes terminam de se
afastar, e o astronauta só reage (acompanha com a cabeça e depois acena) depois
que a decolagem começa e termina. Os dois elementos compartilham a mesma
máquina de estados, portanto não são movimentos independentes. Tudo é calculado
com o tempo decorrido (delta time) e nada depende da taxa de quadros.

**Pausa:** a tecla **P** congela o tempo da animação, mas a renderização e os
controles da câmera continuam funcionando. A tecla **R** reinicia a sequência
e retoma a animação.

## Instalação e execução

Requisitos: Python 3.10 ou superior, placa/driver com suporte a OpenGL e
Windows, Linux ou macOS com ambiente gráfico.

Windows (PowerShell, na pasta do projeto):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Se o comando `py` não estiver disponível, crie o ambiente com
`python -m venv .venv`.

Linux e macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

O Pygame cria a janela (960 x 640, redimensionável) e o contexto OpenGL 2.1. Os
shaders são GLSL versão 120, compatíveis com esse contexto. As dependências
estão em `requirements.txt`.

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

## Requisitos do enunciado e onde estão implementados

| Requisito | Como foi atendido | Onde |
|---|---|---|
| 1. Temas reconhecíveis em um ambiente | Foguete e astronauta montados com caixas, cilindros, cones e esferas, em uma base de lançamento lunar | `models/rocket.py`, `models/astronaut.py`, `main.py` |
| 2. Animação e interação, com delta time | Máquina de estados em que cada etapa depende do fim da anterior; tempo vem de `clock.tick` | `animation/state_machine.py`, `main.py` |
| 3. Translação, rotação, escala e hierarquia | `Object3D` com filhos; matriz local = T · R · S, multiplicada pela matriz do pai | `core/object3d.py`, `core/matrix.py` |
| 4. Câmera em perspectiva, teclado e pausa | `Camera` filha de um `MovementRig`; pausa zera apenas o delta time da animação | `camera/`, `main.py` |
| 5. Textura de imagem com UV | Textura do solo (256 x 256, gerada com NumPy e enviada como imagem RGB), repetida 8 x 8 por UV; textura da chama | `environment/terrain.py`, `core/texture.py`, `geometries/plane.py` |
| 6. Luz direcional, materiais e normais | Termo difuso (Lambert) e especular (Phong), normais por vértice em todas as primitivas | `core/renderer.py`, `materials/`, `geometries/` |
| 7. Sombra projetada com shadow mapping | Passe de profundidade a partir da luz e comparação no fragment shader, refeitos a cada quadro | `core/renderer.py`, `core/shadow_map.py` |

## Recursos gráficos: arquivos, classes e funções

| Recurso | Arquivos e implementação |
|---|---|
| Aplicação, janela e loop | `main.py`, função `main()` |
| Grafo de cena e transformações hierárquicas | `core/object3d.py`, classe `Object3D`; `core/scene.py`, classe `Scene`; `core/matrix.py`, classe `Matrix` |
| Renderer, shaders de iluminação e shadow mapping | `core/renderer.py`, classe `Renderer` |
| Framebuffer e textura de profundidade | `core/shadow_map.py`, classe `ShadowMap` |
| Buffers de atributos e uniforms GLSL | `core/attribute.py`, classe `Attribute`; `core/uniform.py`, classe `Uniform` |
| Compilação e ligação de shaders | `core/opengl_utils.py`, classe `OpenGLUtils` |
| Luz direcional | `core/light.py`, classe `DirectionalLight` |
| Câmera em perspectiva e navegação | `camera/camera.py`, classe `Camera`; `camera/movement_rig.py`, classe `MovementRig` |
| Primitivas | `geometries/box.py` (`Box`), `cylinder.py` (`Cylinder`), `sphere.py` (`Sphere`), `cone.py` (`Cone`) e `plane.py` (`Plane`) |
| Materiais Lambert e Phong | `materials/lambert.py` (`LambertMaterial`) e `materials/phong.py` (`PhongMaterial`) |
| Texturas | `core/texture.py`, classe `Texture`; `environment/terrain.py`, funções `create_lunar_texture()` e `create_flame_texture()` |
| Foguete hierárquico | `models/rocket.py`, classe `Rocket`; métodos `set_support_angle()` e `set_flame_scale()` |
| Astronauta hierárquico | `models/astronaut.py`, classe `Astronaut`; métodos `set_arm_swing()`, `set_leg_swing()`, `set_raised_arm_angle()`, `set_head_yaw()` e `set_body_yaw()` |
| Sequência de animação | `animation/state_machine.py`, enumeração `AnimationState` e classe `StateMachine`; `reset()` reinicia e `update()` avança o tempo e os estados |

## Shaders, atributos e uniforms

Os shaders ficam como strings dentro da classe `Renderer`
(`core/renderer.py`), em GLSL 120. Há dois programas:

| Shader | Constante | Função |
|---|---|---|
| Vertex de sombra | `SHADOW_VERTEX_SHADER` | Transforma cada vértice por `u_light_space_matrix * u_model`, ou seja, para o ponto de vista da luz. |
| Fragment de sombra | `SHADOW_FRAGMENT_SHADER` | Vazio: só a profundidade é gravada na textura do framebuffer. |
| Vertex principal | `VERTEX_SHADER` | Calcula posição em tela, posição e normal no mundo, UV e posição no espaço da luz. |
| Fragment principal | `FRAGMENT_SHADER` | Aplica textura ou cor, iluminação ambiente, difusa e especular, e o fator de sombra. |

**Atributos de vértice:** `a_position` (posição), `a_uv` (coordenada de textura,
quando existe) e `a_normal` (normal). O shader de sombra usa apenas `a_position`.

**Uniforms do shader principal:**

- Transformação: `u_model`, `u_view`, `u_projection`, `u_normal_matrix`, `u_light_space_matrix`.
- Material e textura: `u_color`, `u_texture`, `u_use_texture`, `u_material_model`, `u_specular_color`, `u_shininess`.
- Iluminação e câmera: `u_light_direction`, `u_light_color`, `u_ambient_strength`, `u_camera_position`.
- Sombra: `u_shadow_map`, `u_shadow_texel_size`.

**Relação com as transformações:** cada objeto tem uma matriz de mundo, obtida
multiplicando as matrizes locais ao longo da hierarquia (`Object3D.iter_objects`).
Ela vai para `u_model`. A câmera fornece `u_view` (inversa da sua matriz de
mundo) e `u_projection` (perspectiva). A normal usa a inversa transposta da
parte 3 x 3 da matriz de mundo (`u_normal_matrix`), o que mantém as normais
corretas quando há escala não uniforme.

## Sombreamento e sombra projetada

- **Sombreamento (shading):** cálculo da luz na própria superfície, no fragment
  shader. O termo difuso é `max(dot(normal, direção_da_luz), 0)`; para
  materiais Phong soma-se um termo especular que depende da direção do
  observador. Depende só da normal, da luz e da câmera.
- **Sombra projetada:** um objeto impedindo a luz de chegar a outra superfície.
  Exige saber o que a luz "enxerga". Por isso a cena é renderizada primeiro do
  ponto de vista da luz (projeção ortográfica, pois a luz é direcional) em uma
  textura de profundidade de 2048 x 2048. No passe principal, cada fragmento é
  levado ao espaço da luz e sua profundidade é comparada com a do mapa; se
  houver algo mais próximo da luz, o fragmento está na sombra.

Detalhes da implementação: o `bias` depende do ângulo entre a normal e a luz
(evita o "acne" de sombra) e a comparação é feita em 9 amostras vizinhas
(PCF 3 x 3), o que suaviza a borda. A sombra reduz apenas a luz direta; a luz
ambiente não é afetada. Como o mapa é refeito a cada quadro, a sombra acompanha
o foguete e o astronauta durante a animação.

## Adaptações em relação ao livro

O framework segue a ideia e os nomes principais do livro de Stemkoski e
Pascale (`Object3D`, `Attribute`, `Uniform`, `Matrix`, `Camera`, `MovementRig`,
`OpenGLUtils`), mas foi reescrito de forma simplificada para este trabalho:

- as primitivas são subclasses de `Object3D` (classe `Geometry`) e guardam também cor, textura e material, em vez de separar `Mesh`, `Geometry` e `Material`;
- há um único renderer com dois programas de shader, em GLSL 120 e não 330, para funcionar em contextos OpenGL 2.1;
- o shadow mapping (seção 6.9) segue a mesma ideia do livro (passe de profundidade pela luz, matriz da luz, comparação com bias), mas implementado direto no `Renderer`, com PCF 3 x 3.

## Contribuições individuais

| Integrante | Contribuições |
|---|---|
| Taagny Augusto | Modelo e animação do foguete (`models/rocket.py`); ambiente, plataforma, painel de controle e texturas (`environment/terrain.py`, `main.py`); materiais e luz (`materials/`, `core/light.py`). |
| Gustavo Aliani | Modelo e animação do astronauta (`models/astronaut.py`); máquina de estados e delta time (`animation/state_machine.py`); câmera e controles (`camera/`); shadow mapping (`core/shadow_map.py`, `core/renderer.py`). |

Os dois integrantes revisaram o código integrado e participaram dos testes e da
documentação.

## Fontes e créditos

- STEMKOSKI, Lee; PASCALE, Michael. *Developing graphics frameworks with Python and OpenGL*. 1. ed. Boca Raton: CRC Press, 2022. DOI: 10.1201/9781003181378. Referência de arquitetura e do shadow mapping (seção 6.9).
- As texturas do terreno e da chama são procedurais, geradas em `environment/terrain.py`; não utilizam imagens de terceiros.
- Pygame-ce: <https://pyga.me/docs/>
- PyOpenGL: <https://pyopengl.sourceforge.net/>
- NumPy: <https://numpy.org/doc/>
- OpenGL e GLSL: <https://www.khronos.org/opengl/>

## Declaração de uso de inteligência artificial

| Item | Descrição |
|---|---|
| Ferramenta | Claude (Anthropic) |
| Finalidade | Elaboração dos prompts de desenvolvimento por etapas, análise de conformidade do projeto com o enunciado, revisão do código e redação deste README. |
| Trechos | Documentação (`README.md`) e revisão geral do projeto. |
| Ferramenta usada para gerar o código | PyCharm |
| Trechos gerados ou revisados com apoio de IA | Estrutura do framework (`core/`), primitivas (`geometries/`), modelos (`models/`), máquina de estados (`animation/`), shaders e shadow mapping (`core/renderer.py`, `core/shadow_map.py`). |

O código foi integrado e testado no projeto, e os integrantes o revisaram e
conseguem explicar seu funcionamento.
