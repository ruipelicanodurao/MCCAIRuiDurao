"""Instalação procedural inspirada na fotografia. Executar no Blender.
Dimensões aproximadas, em metros. Não requer bibliotecas externas.
"""
import bpy
import math
import random
from pathlib import Path
from mathutils import Vector
 
# CONFIGURAÇÃO
VIDEO_PATH = r""  # Exemplo: C:\Videos\instalacao.mp4
OUTPUT_BLEND = r""  # Opcional: caminho absoluto para guardar o .blend
RENDER_IMAGE = r""  # Opcional: caminho absoluto para render PNG
PALAVRAS = ["MEMÓRIA", "PARTILHA", "FUTURO", "CULTURA", "EMOÇÃO",
            "HISTÓRIA", "IDENTIDADE", "CONEXÃO", "VOZ", "DESCOBERTA"]
SENSOR_ATIVO = 2  # 0 a 4; apenas demonstração visual
MOSTRAR_FLUXOS = True
SKY_BLUE = (0.235, 0.617, 0.831, 1)  # Aproximação linear de #87CEEB
random.seed(12)
 
# Substitui apenas a coleção desta instalação.
NAME = "Instalacao_Procedural"
old = bpy.data.collections.get(NAME)
if old:
    for obj in list(old.all_objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
collection = bpy.data.collections.new(NAME)
bpy.context.scene.collection.children.link(collection)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.fps = 25
scene.frame_start = 1
scene.frame_end = 250
scene.world = bpy.data.worlds.new("Ambiente_Instalacao")
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.025, 0.035, 0.05, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.25
try:
    scene.view_settings.view_transform = 'AgX'
except TypeError:
    pass
 
def move_collection(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj
 
def solid(name, color, roughness=0.5, metallic=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = color
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    m.diffuse_color = color
    return m
 
def emission(name, color, strength=2):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    em = n.new('ShaderNodeEmission')
    em.inputs[0].default_value = color
    em.inputs[1].default_value = strength
    m.node_tree.links.new(em.outputs[0], out.inputs['Surface'])
    return m
 
def transparent(name, color, visibility=0.08):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    mix = n.new('ShaderNodeMixShader')
    tr = n.new('ShaderNodeBsdfTransparent')
    em = n.new('ShaderNodeEmission')
    em.inputs[0].default_value = color
    em.inputs[1].default_value = 0.7
    mix.inputs[0].default_value = visibility
    m.node_tree.links.new(tr.outputs[0], mix.inputs[1])
    m.node_tree.links.new(em.outputs[0], mix.inputs[2])
    m.node_tree.links.new(mix.outputs[0], out.inputs['Surface'])
    return m
 
black = solid('Preto_mate', (0.009, 0.009, 0.011, 1), 0.92)
paper = solid('Papel_marfim', (0.69, 0.53, 0.32, 1), 0.85)
cover = solid('Capa_castanha', (0.12, 0.045, 0.018, 1), 0.8)
ink = solid('Texto_pagina', (0.05, 0.025, 0.012, 1), 0.9)
floor_mat = solid('Pavimento_escuro', (0.045, 0.052, 0.06, 1), 0.23)
wall_mat = solid('Paredes_galeria', (0.06, 0.065, 0.07, 1), 0.88)
cyan = emission('Luz_sky_blue', SKY_BLUE, 3)
purple = emission('Luz_violeta', (0.30, 0.035, 0.9, 1), 3)
white = emission('Texto_holografico', (0.55, 0.85, 1, 1), 2)
shell = transparent('Cubo_transparente_azulado', SKY_BLUE, 0.035)
screen = transparent('Tela_transparente', SKY_BLUE, 0.08)
 
def box(name, loc, size, mat, bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = move_collection(bpy.context.object)
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if parent:
        o.parent = parent
    o.location = loc
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Arestas', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    return o
 
def line(name, points, radius, mat, parent=None):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = radius
    data.bevel_resolution = 3
    sp = data.splines.new('POLY')
    sp.points.add(len(points)-1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.parent = parent
    data.materials.append(mat)
    return obj
 
def text(name, body, loc, size, mat, rotation=(0,0,0), parent=None):
    data = bpy.data.curves.new(name, 'FONT')
    data.body = body
    data.size = size
    data.align_x = 'CENTER'
    data.align_y = 'CENTER'
    data.extrude = 0.0003
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rotation
    data.materials.append(mat)
    return obj
 
# Galeria simplificada, sem pessoas nem reprodução de quadros.
box('Pavimento', (0, 1, -0.09), (11, 12, 0.18), floor_mat)
box('Parede_fundo', (0, 5, 2.3), (11, 0.18, 4.6), wall_mat)
box('Parede_lateral', (-5.4, 1, 2.3), (0.18, 8, 4.6), wall_mat)
for x in (-4, -1.8, 1.8, 4):
    box('Painel_galeria', (x, 4.87, 2.15), (1.1, 0.035, 1.5), black)
 
# Livro e pódio preto mate.
book_x, book_y = -1.25, -0.45
box('Podio_livro_PRETO_MATE', (book_x, book_y, 0.58), (0.48, 0.48, 1.16), black)
root = bpy.data.objects.new('Livro_inclinacao', None)
collection.objects.link(root)
root.location = (book_x, book_y, 1.20)
root.rotation_euler.x = math.radians(20)
box('Apoio_inclinado_PRETO_MATE', (0,0,0), (1.24,0.85,0.045), black, parent=root)
box('Capa_livro', (0,0,0.035), (1.18,0.79,0.04), cover, parent=root)
for side in (-1, 1):
    page = box('Paginas_esquerda' if side < 0 else 'Paginas_direita',
               (side*0.29,0,0.09), (0.565,0.74,0.075), paper, 0.012, root)
    # Linhas discretas sugerindo as folhas empilhadas.
    for z in (0.065, 0.077, 0.089, 0.101):
        line('Folhas', [(side*0.565,-0.37,z),(side*0.025,-0.37,z)], 0.0007, cover, root)
line('Vinco_central', [(0,-0.37,0.135),(0,0.37,0.135)], 0.006, cover, root)
text('Titulo_livro', 'UM LIVRO DE MEMÓRIAS', (-0.28,0.26,0.133), 0.035, ink, parent=root)
for i, word in enumerate(['Recordar','Descobrir','Sentir','Partilhar','Imaginar']):
    y = 0.18-i*0.105
    text('Opcao_'+str(i), word, (-0.28,y,0.133), 0.029, ink, parent=root)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.026, depth=0.004)
    sensor = move_collection(bpy.context.object)
    sensor.name = 'Sensor_pressao_'+str(i+1)
    sensor.parent = root
    sensor.location = (0.42,y,0.132)
    sensor.data.materials.append(black)
    sensor['tipo'] = 'Sensor de pressão conceptual; sem ligação física'
    sensor['canal'] = i+1
    pts = [(0.42+0.033*math.cos(a*math.tau/64),
            y+0.033*math.sin(a*math.tau/64),0.136) for a in range(65)]
    line('Indicador_sensor_'+str(i+1), pts, 0.002, cyan if i==SENSOR_ATIVO else white, root)
text('Texto_pagina_direita', 'ESCUTA\n\nCada toque desperta\numa nova memória.',
     (0.27,0.27,0.134), 0.033, ink, parent=root)
 
# Poste preto mate e cubo: aresta 0,9 m.
cx, cy, cz = 1.0, 0.7, 2.02
half = 0.45
box('Poste_cubo_PRETO_MATE', (cx,cy,0.785), (0.32,0.32,1.57), black)
box('Cubo_casca_transparente', (cx,cy,cz), (0.9,0.9,0.9), shell, 0)
for axis in range(3):
    others = [a for a in range(3) if a != axis]
    for s1 in (-1,1):
        for s2 in (-1,1):
            a = [cx,cy,cz]; b = a.copy()
            a[axis] -= half; b[axis] += half
            a[others[0]] += s1*half; b[others[0]] += s1*half
            a[others[1]] += s2*half; b[others[1]] += s2*half
            line('Aresta_cubo', [a,b], 0.006, cyan)
 
# Painel vertical com UV explícito; normal orientada para a câmara (-Y).
def panel(name, center, width, height, mat):
    x,y,z = center
    verts = [(x-width/2,y,z-height/2),(x+width/2,y,z-height/2),
             (x+width/2,y,z+height/2),(x-width/2,y,z+height/2)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [(0,1,2,3)])
    mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        for li, coord in zip(poly.loop_indices, [(0,0),(1,0),(1,1),(0,1)]):
            uv.data[li].uv = coord
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj
 
# Vídeo no painel interior traseiro, sem tapar a tela frontal.
video_mat = emission('Video_placeholder_sky_blue', SKY_BLUE, 0.65)
if VIDEO_PATH:
    path = Path(bpy.path.abspath(VIDEO_PATH))
    if not path.is_file():
        raise FileNotFoundError('Vídeo inexistente: '+str(path))
    image = bpy.data.images.load(str(path), check_existing=True)
    image.source = 'MOVIE'
    nodes = video_mat.node_tree.nodes
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.image_user.use_auto_refresh = True
    tex.image_user.use_cyclic = True
    tex.image_user.frame_start = 1
    tex.image_user.frame_duration = max(1, image.frame_duration)
    video_mat.node_tree.links.new(tex.outputs['Color'], nodes.get('Emission').inputs[0])
panel('Video_interior_cubo', (cx,cy+0.40,cz), 0.82,0.82,video_mat)
panel('Tela_transparente_word_cloud', (cx,cy-0.455,cz), 0.83,0.83,screen)
 
# Nuvem de palavras tipográfica, editável. Palavras de exemplo.
layout = [(0,0.22,0.071),(-0.15,0.12,0.039),(0.13,0.10,0.045),
          (0,-0.01,0.077),(-0.18,-0.12,0.036),(0.15,-0.13,0.037),
          (0,-0.23,0.046),(-0.19,-0.30,0.027),(0.21,0.30,0.033),(0.16,-0.31,0.026)]
for i,(word,(dx,dz,size)) in enumerate(zip(PALAVRAS,layout)):
    text('WordCloud_'+str(i),word,(cx+dx,cy-0.465,cz+dz),size,
         white if i%3 else cyan,(math.pi/2,0,0))
 
# Fluxos luminosos decorativos, inspirados na referência.
if MOSTRAR_FLUXOS:
    for j in range(18):
        points=[]
        for k in range(65):
            t=k/64
            fade=math.sin(math.pi*t)
            x=-0.78+1.32*t
            y=-0.15+0.84*t+0.15*math.sin(t*8+j)*fade
            z=1.38+0.62*t+0.19*math.sin(t*9+j*0.45)*fade
            points.append((x,y,z))
        line('Fluxo_'+str(j),points,0.0018,cyan if j%3 else purple)
 
def light(name, loc, energy, color, size=1, target=None, kind='AREA'):
    data=bpy.data.lights.new(name,kind)
    data.energy=energy
    data.color=color
    if kind=='AREA': data.shape='DISK'; data.size=size
    else: data.shadow_soft_size=size
    obj=bpy.data.objects.new(name,data)
    collection.objects.link(obj)
    obj.location=loc
    if target:
        obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
 
light('Luz_livro',(-2,-2,4),450,(1,0.75,0.48),3,(-1,0,1))
light('Luz_ambiente',(2,-1,4.2),350,(0.65,0.8,1),4,(0,1,1))
light('Interior_sky_blue',(cx,cy,cz),18,(0.53,0.81,0.92),0.2,kind='POINT')
light('Luz_fundo',(0,3.5,3.6),220,(1,0.7,0.45),2,(0,4.8,2))
cam_data=bpy.data.cameras.new('Camera_instalacao')
cam=bpy.data.objects.new('Camera_instalacao',cam_data)
collection.objects.link(cam)
cam.location=(4.0,-7.5,3.3)
cam.rotation_euler=(Vector((-0.15,0.5,1.4))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=47
scene.camera=cam
scene.frame_set(1)
 
# Não guarda nem renderiza automaticamente, salvo configuração explícita.
if OUTPUT_BLEND:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUTPUT_BLEND))
if RENDER_IMAGE:
    scene.render.filepath=bpy.path.abspath(RENDER_IMAGE)
    scene.render.image_settings.file_format='PNG'
    bpy.ops.render.render(write_still=True)
print('Instalação criada. Numpad 0: câmara. F12: render.')
