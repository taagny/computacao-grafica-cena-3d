# ARES — Operação Horizonte

Trabalho prático de Computação Gráfica · Ciência da Computação · UNIPAC · 2026/02.

## Integrantes e temas

| Integrantes | Temas da cena |
|---|---|
| Taagny Augusto e Gustavo Aliani | **18 — Rover explorador** e **3 — Drone de quatro hélices** |

Os temas foram escolhidos livremente, conforme autorização do professor informada pelo aluno, em substituição ao sorteio. A cena mantém dois modelos distintos, ambos animados e envolvidos em uma ação conjunta.

## Cena e interação

Uma estação de pesquisa em Marte recebe o rover **R-01** e o drone **D-04**. O rover percorre um corredor até o ponto de inspeção. Sua chegada libera a decolagem do drone, que orbita o veículo com a câmera orientada para ele. O sensor do rover acompanha a posição do drone. Após a confirmação da leitura, os dois avançam juntos; somente quando o rover para na posição segura o drone retorna e pousa.

O ambiente inclui terreno rochoso, estação modular, antena, painéis solares, plataforma de pouso, equipamentos e balizas. Os modelos são construídos por composição de caixas, cilindros, esferas, planos e malhas do framework, sem modelos 3D importados.

| Etapa | Intervalo | Ação coordenada |
|---|---|---|
| Sistemas prontos | 0–2,5 s | Rover e drone aguardam |
| Aproximação | 2,5–8,5 s | Rover avança; drone permanece na plataforma |
| Decolagem | 8,5–12 s | Chegada do rover libera a saída do drone |
| Varredura orbital | 12–20 s | Drone inspeciona; rover permanece parado e acompanha com o sensor |
| Enlace confirmado | 20–23 s | Drone aguarda o sinal do sensor |
| Exploração conjunta | 23–29,5 s | Rover avança com o drone em posição relativa de escolta |
| Retorno à base | 29,5–34 s | Rover para; drone retorna e pousa |
| Missão concluída | A partir de 34 s | Pose final mantida até reiniciar |

As etapas dependem do término das anteriores: não são dois movimentos independentes. `Mission.update(dt)` acumula segundos e calcula o progresso de cada etapa. A função `smooth(t) = t²(3−2t)` suaviza as transições, e o ângulo das rodas deriva da distância percorrida dividida pelo raio. Os rotores têm aceleração e desaceleração integradas analiticamente. Não há simulação física ou detecção de colisões, que não são obrigatórias no enunciado.

## Instalação e execução

Requisitos: **Python 3.10 ou superior**, ambiente gráfico e driver com shaders GLSL e framebuffer de profundidade. A aplicação solicita OpenGL 2.1, usa GLSL 120 e precisa das funções de framebuffer disponíveis no driver. Foi validada no Windows com Python 3.14.7 e contexto OpenGL 4.6 de compatibilidade em uma Radeon RX 6600. Linux e macOS não foram testados.

Baixe ou clone o repositório e extraia os arquivos antes de executar. No PowerShell, dentro da pasta do projeto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Se `py` não estiver disponível, use `python -m venv .venv` no primeiro comando.

Em Linux/macOS com driver compatível:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

As dependências são Pygame-ce, PyOpenGL, NumPy e Pillow, especificadas em `requirements.txt`. A instalação requer internet; a execução funciona offline. As texturas são carregadas a partir da pasta do código, independentemente da pasta de onde o programa é iniciado. A janela inicial é de 1440 × 900 pixels e pode ser redimensionada. O programa solicita MSAA 4× e tenta novamente sem MSAA caso o driver não o suporte.

## Controles

| Controle | Ação |
|---|---|
| W / S e A / D | Avançar/recuar e deslocar lateralmente a câmera |
| Q / E | Descer/subir a câmera |
| Setas | Orientar a câmera |
| Shift | Acelerar o deslocamento da câmera |
| 1 / 2 / 3 | Vistas geral, rover e base |
| C | Ativar/desativar órbita automática da câmera |
| P ou Espaço | Pausar/retomar a missão |
| R | Reiniciar todos os movimentos e retomar |
| L | Alternar sombra projetada para comparação didática |
| H | Mostrar/ocultar ajuda |
| F12 | Salvar captura em `artifacts/` |
| Esc | Fechar |

O painel também oferece botões para pausa, reinício e ajuda. A pausa zera apenas o delta time da missão: a câmera e a renderização continuam funcionando. O movimento manual da câmera encerra sua órbita automática.

## Requisitos e localização no código

| Requisito | Implementação | Arquivos, classes ou funções |
|---|---|---|
| 1. Dois temas reconhecíveis em um ambiente | Rover com seis rodas e sensor; drone com quatro rotores e câmera; estação marciana | `models/rover.py`: `Rover`; `models/drone.py`: `Drone`; `environment/mars.py`: `build_scene` |
| 2. Ambos animados, com interação e tempo decorrido | Etapas com espera, chegada, inspeção, confirmação e escolta | `animation/mission.py`: `Mission.update`, `Mission.STAGES` |
| 3. Translação, rotação, escala e hierarquia | Matrizes locais e de mundo; rodas, sensor, rotores e gimbal com pivôs próprios | `core/object3d.py`: `Object3D`; `core/matrix.py`: `Matrix`; `models/primitives.py`: `pivot` |
| 4. Perspectiva, teclado, pausa e retomada | Câmera sob um rig; tempo da câmera separado do tempo da missão | `camera/camera.py`: `Camera`; `camera/movement_rig.py`: `MovementRig`; `main.py`: `main` |
| 5. Textura de imagem visível com UV | PNGs no chão, nos painéis solares e na placa da estação | `assets/textures/`; `geometries/plane.py`: `Plane`; `core/texture.py`: `Texture`; `environment/mars.py`: `image_texture` |
| 6. Luz direcional, materiais e normais | Difuso Lambert, especular Phong e normais transformadas por inversa transposta | `core/light.py`: `DirectionalLight`; `materials/`; `geometries/`; `core/renderer.py`: `Renderer` |
| 7. Sombra projetada por elemento animado | Shadow mapping com passe de profundidade 2048² atualizado a cada quadro, bias e PCF 3×3 | `core/shadow_map.py`: `ShadowMap`; `core/renderer.py`: `_render_shadow_depth`, `render` |

## Framework, transformações e renderização

O framework preserva e adapta componentes do projeto original, inspirado na arquitetura do livro indicado no enunciado. Não é uma reprodução integral do framework da obra: as primitivas são objetos de cena que armazenam geometria e material, e os shaders usam GLSL 120. A atividade permite adaptações e dispensa a reconstrução integral do framework.

`Object3D` organiza objetos por relações de pai e filho. A matriz local é `T · Rz · Ry · Rx · S`; a matriz de mundo do filho é a matriz de mundo do pai multiplicada pela matriz local do filho. Com vetores coluna, a escala atua primeiro, depois rotação e translação. Assim, as rodas acompanham o rover e continuam girando em seus eixos locais. O sensor, o gimbal e os rotores mantêm articulações próprias.

`Camera.view_matrix()` inverte a transformação de mundo da câmera. `Matrix.perspective()` calcula a projeção. A posição final é `P · V · M · posição_local`. As normais usam a inversa transposta da parte linear de `M` para permanecerem perpendiculares às superfícies sob escala não uniforme.

`core/batching.py`: `batch_static` aplica uma vez as transformações das peças fixas e agrupa suas malhas por material. As normais são transformadas antes da concatenação; os pivôs animados são preservados. Isso reduz chamadas de desenho sem substituir a modelagem por primitivas.

Em cada quadro, `main` lê os eventos e o delta time, atualiza missão e câmera, chama o renderer, compõe o painel e apresenta a imagem. O loop limita o passo a 0,1 s para evitar saltos após interrupções prolongadas da janela; sob esses travamentos, o tempo da missão avança mais devagar que o relógio de parede. Em funcionamento normal, a animação depende de segundos, não do número de quadros. `Mission` também aceita passos longos e atravessa as etapas corretamente.

## Shaders, atributos e uniforms utilizados

Os shaders são strings GLSL incluídas no código-fonte. `core/opengl_utils.py`: `OpenGLUtils.create_program` verifica sua compilação e ligação. Não há arquivos de shader externos necessários.

| Programa | Localização | Vertex shader | Fragment shader |
|---|---|---|---|
| Principal | `core/renderer.py`: `VERTEX_SHADER`, `FRAGMENT_SHADER` | Transforma posição, normal, UV e posição no espaço da luz | Calcula imagem/cor, Lambert/Phong, sombra, emissão, varredura e névoa |
| Sombra | `core/renderer.py`: `SHADOW_VERTEX_SHADER`, `SHADOW_FRAGMENT_SHADER` | Aplica `u_light_space_matrix * u_model` | Corpo vazio: o pipeline grava a profundidade |
| Céu | `core/sky.py`: `Sky.VERTEX`, `Sky.FRAGMENT` | Desenha um quadrilátero na tela | Calcula raios orientados pela câmera, gradiente e estrelas |
| Painel | `core/hud.py`: `HUD.VERTEX`, `HUD.FRAGMENT` | Desenha um quadrilátero com UV | Amostra a imagem RGBA do painel, composta com mistura alfa |

**Atributos por vértice**, enviados a VBOs por `core/attribute.py`: `Attribute`:

| Atributo | Componentes | Uso |
|---|---|---|
| `a_position` | 3 floats | Posição local da malha; também usada no passe de sombra |
| `a_normal` | 3 floats | Normal para calcular a iluminação da superfície |
| `a_uv` | 2 floats | Coordenada na imagem; nas peças sem imagem agrupadas, recebe zero |

Caixas têm normais por face; esferas e cilindros usam normais analíticas. Rochas e relevo usam o produto vetorial dos lados dos triângulos. `geometries/torus.py`: `Torus` calcula posições, normais e UV parametricamente. Os quadriláteros do céu e do painel usam apenas `a_position` de duas componentes, em seus próprios programas.

**Uniforms do programa principal**, enviados pela aplicação por `core/uniform.py`: `Uniform`:

| Uniforms | Finalidade |
|---|---|
| `u_model`, `u_view`, `u_projection` | Matrizes de modelo, vista e perspectiva |
| `u_normal_matrix` | Inversa transposta da parte linear da matriz de modelo, embutida em 4×4 |
| `u_light_space_matrix` | Projeção ortográfica da luz multiplicada por sua vista |
| `u_color`, `u_texture`, `u_use_texture` | Cor base, imagem na unidade 0 e seletor de imagem |
| `u_material_model`, `u_specular_color`, `u_shininess` | Lambert/Phong, cor especular e expoente de brilho |
| `u_light_direction`, `u_light_color`, `u_ambient_strength` | Direção e cor da luz e contribuição ambiente |
| `u_camera_position` | Posição da câmera para especular e névoa |
| `u_shadow_map`, `u_shadow_texel_size` | Profundidade na unidade 1 e deslocamento de amostras PCF |
| `u_shadows_enabled` | Ativação da sombra projetada |
| `u_emission` | Mistura com a cor não atenuada pela iluminação |
| `u_fog_color` | Cor da névoa distante |
| `u_scan`, `u_time` | Ativação da faixa de inspeção no rover e tempo da missão |

O programa de sombra usa `u_model` e `u_light_space_matrix`. O céu usa `u_right`, `u_up`, `u_forward` e `u_projection`; nesse programa separado, `u_projection` é um vetor de duas escalas. O painel usa `image`, sampler na unidade 0. Atributos fornecem dados por vértice; uniforms fornecem parâmetros constantes durante cada desenho. Os dados interpolados entre vertex e fragment shader são declarados como `varying` em GLSL 120.

## Sombreamento de superfície e sombra projetada

**Sombreamento da superfície:** calcula a resposta local do material à luz. O difuso Lambert usa `max(dot(N,L),0)`. Phong acrescenta um termo especular que depende da direção refletida, da direção do observador e do expoente de brilho. As normais são normalizadas no fragment shader. Uma contribuição ambiente e um preenchimento azulado evitam superfícies inteiramente pretas.

**Sombra projetada:** identifica se outra geometria bloqueia a luz antes de ela chegar à superfície. A implementação segue a abordagem de shadow mapping solicitada pelo enunciado, que indica a seção 6.9 do livro:

1. O renderer desenha a geometria do ponto de vista da luz direcional, com projeção ortográfica, em uma textura de profundidade de **2048 × 2048** pixels anexada a um framebuffer.
2. No passe principal, transforma cada fragmento para o mesmo espaço da luz, divide por `w`, remapeia para [0,1] e compara sua profundidade com a gravada. Se houver uma superfície mais próxima da luz, o fragmento perde a contribuição direta.

O mapa é refeito a cada quadro com as poses atuais, de modo que as sombras do rover e do drone acompanham o movimento. Um bias dependente da normal reduz auto-sombra incorreta; PCF 3×3 calcula a média de nove comparações para suavizar bordas. A contribuição ambiente é mantida. A tecla **L** permite comparar a cena com e sem sombra projetada, preservando a iluminação da superfície.

## Texturas e recursos adicionais

As três imagens RGB entregues são originais, produzidas por programação com NumPy e Pillow:

| Imagem | Origem e aplicação |
|---|---|
| `assets/textures/martian_regolith.png` | Ruído com semente fixa, ondulações e grãos; aplicada repetidamente no chão por UV |
| `assets/textures/solar_cells.png` | Grade de células desenhada por programação; aplicada nos painéis solares |
| `assets/textures/station_sign.png` | Identificação da estação desenhada por programação; aplicada na placa |

`image_texture` carrega os PNGs e inverte suas linhas para a convenção OpenGL. `Texture` envia os pixels à GPU com `glTexImage2D`. Nenhuma imagem ou modelo de terceiros precisa ser baixado durante a execução. O painel usa fontes do sistema com alternativas; não são distribuídos arquivos de fontes comerciais.

Recursos extras integrados à cena:

- **Varredura procedural:** durante a inspeção, a altura `0.3 + mod(u_time * 0.65, 2.7)` e `smoothstep` definem uma faixa ciano sobre os fragmentos do rover.
- **Névoa:** mistura a cor iluminada à cor distante por `1−exp(−k·d²)`, com `d` igual à distância até a câmera.
- **Céu procedural:** gradiente dependente da direção de visão e estrelas geradas por hash em células angulares.
- **Indicadores emissivos e painel:** cores não atenuadas pela iluminação e uma imagem RGBA de interface composta sobre a cena.

Esses efeitos complementam os requisitos. Os indicadores emissivos não iluminam objetos vizinhos; não há bloom, bump mapping nem simulação física da atmosfera. A atribuição de eventual bônus cabe ao professor.

## Verificação da execução

A lógica foi verificada localmente em sete testes: independência de taxa de quadros (24, 30, 60 e 144 FPS), dependências entre etapas, pausa, reinício, passo longo até a conclusão, continuidade e rejeição de tempo inválido. A aplicação também passou por verificação de controles e redimensionamento e por renderização real de doze capturas cobrindo etapas, vistas e comparação de sombras. Os testes e relatórios auxiliares de desenvolvimento não são necessários para executar a entrega.

Para reproduzir a verificação gráfica com o código entregue:

```powershell
.\.venv\Scripts\python.exe main.py --verify --hidden
```

O comando requer contexto OpenGL mesmo com janela oculta e salva doze capturas em `artifacts/`. Para abrir diretamente na inspeção: `python main.py --time 16 --view 2`. Para uma execução curta com encerramento automático: `python main.py --frames 180 --hidden`.

## Contribuições individuais e uso de inteligência artificial

| Integrante | Contribuição informada |
|---|---|
| Taagny Augusto | Desenvolvimento da cena, integração, modelagem, animação, ambiente, interface, adaptações do framework, verificações e documentação, com apoio de IA |
| Gustavo Aliani | Identificado como integrante da entrega; não foram informadas contribuições individuais |

O desenvolvimento foi informado como realizado por Taagny. Não são atribuídas a Gustavo tarefas que não foram relatadas. A identificação de dois integrantes não substitui a exigência do enunciado de participação e domínio individual na apresentação.

**Ferramenta de IA:** Codex, da OpenAI. **Finalidade:** analisar o PDF fornecido, adaptar o projeto, desenvolver e revisar código, gerar imagens por programação, executar verificações e redigir documentação. **Trechos desenvolvidos ou revisados com esse apoio:** `main.py`, `animation/mission.py`, `models/rover.py`, `models/drone.py`, `models/primitives.py`, `environment/mars.py`, `geometries/torus.py`, `core/batching.py`, `core/hud.py`, `core/sky.py`, ajustes em `core/object3d.py`, `core/renderer.py` e `camera/movement_rig.py`, imagens em `assets/textures/` e este README. Os componentes de framework preservados vêm do projeto original recebido.

O enunciado permite IA mediante declaração, mas exige revisão e capacidade de explicar o funcionamento. Esta documentação não atesta que os integrantes já realizaram essa preparação individual.

## Fontes e créditos

- **Enunciado fornecido:** *Trabalho — Computação Gráfica*, 2026/02. Fonte dos requisitos e dos temas 3 e 18.
- **Projeto original recebido:** componentes de framework Python/OpenGL desta pasta, preservados e adaptados.
- **Referência bibliográfica indicada no enunciado:** STEMKOSKI, Lee; PASCALE, Michael. *Developing Graphics Frameworks with Python and OpenGL*. 1. ed. Boca Raton: CRC Press, 2022. DOI: [10.1201/9781003181378](https://doi.org/10.1201/9781003181378). A implementação é uma adaptação própria, não uma cópia integral do framework do livro.
- **Bibliotecas utilizadas:** [Pygame-ce](https://pyga.me/), [PyOpenGL](https://pyopengl.sourceforge.net/), [NumPy](https://numpy.org/) e [Pillow](https://python-pillow.org/).
- **Imagens:** procedurais e originais, geradas localmente; não foram utilizados modelos 3D ou imagens de terceiros.
