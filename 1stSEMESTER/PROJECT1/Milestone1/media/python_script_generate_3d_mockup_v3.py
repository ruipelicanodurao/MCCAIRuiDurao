"""Instalação sem o bloco branco. Executar no Blender.
ATENÇÃO: substitui TODOS os objetos da cena ativa.
Se existirem objetos partilhados com outras cenas, interrompe antes de apagar.
Dimensões aproximadas em metros; sensores apenas visuais.
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector
 
VIDEO_PATH = r""
OUTPUT_BLEND = r""
RENDER_IMAGE = r""
CUBO_LADO = 0.90
POSTE_ALTURA = 1.57
FOLGA_LIVRO_CUBO = 0.08
MOSTRAR_FLUXOS = True
SENSOR_ATIVO = 2
PALAVRAS = ['MEMÓRIA','PARTILHA','FUTURO','CULTURA','EMOÇÃO',
            'HISTÓRIA','IDENTIDADE','CONEXÃO','VOZ','DESCOBERTA']
SKY_BLUE = (0.235, 0.617, 0.831, 1)
 
# Limpeza deliberada: remove também o bloco branco externo à coleção anterior.
scene = bpy.context.scene
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
for obj in list(scene.objects):
    if len(obj.users_scene) > 1:
        raise RuntimeError('Objeto partilhado com outra cena: '+obj.name+
                           '. Executa numa cena independente ou num ficheiro novo.')
# Após validar que não há objetos partilhados, remove a cena anterior.
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
collection = bpy.data.collections.new('Instalacao_Sem_Bloco_Branco')
scene.collection.children.link(collection)
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'
scene.cycles.samples=64
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.fps=25
scene.frame_start=1
scene.frame_end=250
scene.world=bpy.data.worlds.new('Ambiente_Instalacao')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.035,.05,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.25
try: scene.view_settings.view_transform='AgX'
except TypeError: pass
 
def move(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj
 
def solid(name,color,roughness=.8):
    m=bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=roughness
    m.diffuse_color=color
    return m
 
def glow(name,color,strength=2,visibility=1):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes; n.clear()
    out=n.new('ShaderNodeOutputMaterial')
    em=n.new('ShaderNodeEmission')
    em.inputs[0].default_value=color; em.inputs[1].default_value=strength
    if visibility < 1:
        tr=n.new('ShaderNodeBsdfTransparent'); mix=n.new('ShaderNodeMixShader')
        mix.inputs[0].default_value=visibility
        m.node_tree.links.new(tr.outputs[0],mix.inputs[1])
        m.node_tree.links.new(em.outputs[0],mix.inputs[2])
        m.node_tree.links.new(mix.outputs[0],out.inputs[0])
    else: m.node_tree.links.new(em.outputs[0],out.inputs[0])
    return m
 
black=solid('Preto_mate',(.009,.009,.011,1),.95)
paper=solid('Papel_marfim',(.69,.53,.32,1),.85)
cover=solid('Capa_castanha',(.12,.045,.018,1))
ink=solid('Tinta',(.05,.025,.012,1),.9)
floor=solid('Pavimento_escuro',(.045,.052,.06,1),.23)
wall=solid('Paredes_galeria',(.06,.065,.07,1),.88)
cyan=glow('Luz_sky_blue',SKY_BLUE,3)
purple=glow('Luz_violeta',(.30,.035,.9,1),3)
white=glow('Texto_holografico',(.55,.85,1,1),2)
screen=glow('Tela_transparente',SKY_BLUE,.7,.045)
 
def box(name,loc,size,mat,bevel=.01,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=move(bpy.context.object); o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.parent=parent; o.location=loc; o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Arestas','BEVEL'); mod.width=bevel; mod.segments=3
    return o
 
def line(name,pts,radius,mat,parent=None):
    d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'
    d.bevel_depth=radius; d.bevel_resolution=3
    s=d.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,co in zip(s.points,pts): p.co=(*co,1)
    o=bpy.data.objects.new(name,d); collection.objects.link(o)
    o.parent=parent; d.materials.append(mat)
    return o
 
def text(name,body,loc,size,mat,rotation=(0,0,0),parent=None):
    d=bpy.data.curves.new(name,'FONT'); d.body=body; d.size=size
    d.align_x='CENTER'; d.align_y='CENTER'; d.extrude=.0003
    o=bpy.data.objects.new(name,d); collection.objects.link(o)
    o.parent=parent; o.location=loc; o.rotation_euler=rotation
    d.materials.append(mat)
    return o
 
def panel(name,center,width,height,mat):
    x,y,z=center
    verts=[(x-width/2,y,z-height/2),(x+width/2,y,z-height/2),
           (x+width/2,y,z+height/2),(x-width/2,y,z+height/2)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],[(0,1,2,3)]); mesh.update()
    uv=mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        for li,co in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]): uv.data[li].uv=co
    o=bpy.data.objects.new(name,mesh); collection.objects.link(o); mesh.materials.append(mat)
    return o
 
# Galeria: apenas pavimento e paredes escuras. Nenhum bloco branco.
box('Pavimento',(0,1,-.09),(11,12,.18),floor)
box('Parede_fundo',(0,5,2.3),(11,.18,4.6),wall)
box('Parede_lateral',(-5.4,1,2.3),(.18,8,4.6),wall)
for x in (-4,-1.8,1.8,4): box('Painel_galeria',(x,4.87,2.15),(1.1,.035,1.5),black)
 
# Poste de secção igual à base do cubo.
cx,cy=0.55,.7
half=CUBO_LADO/2
cz=POSTE_ALTURA+half
box('Poste_cubo_PRETO_MATE',(cx,cy,POSTE_ALTURA/2),
    (CUBO_LADO,CUBO_LADO,POSTE_ALTURA),black)
 
# Livro junto ao cubo, com pódio próprio preto mate.
book_x=cx-half-FOLGA_LIVRO_CUBO-1.24/2
book_y=cy
box('Podio_livro_PRETO_MATE',(book_x,book_y,.58),(.48,.48,1.16),black)
root=bpy.data.objects.new('Livro_inclinacao',None); collection.objects.link(root)
root.location=(book_x,book_y,1.20); root.rotation_euler.x=math.radians(20)
box('Apoio_inclinado_PRETO_MATE',(0,0,0),(1.24,.85,.045),black,parent=root)
box('Capa_livro',(0,0,.035),(1.18,.79,.04),cover,parent=root)
for side in (-1,1):
    box('Paginas_esquerda' if side<0 else 'Paginas_direita',
        (side*.29,0,.09),(.565,.74,.075),paper,.012,root)
    for z in (.065,.077,.089,.101):
        line('Folhas',[(side*.565,-.37,z),(side*.025,-.37,z)],.0007,cover,root)
line('Vinco_central',[(0,-.37,.135),(0,.37,.135)],.006,cover,root)
text('Titulo_livro','UM LIVRO DE MEMÓRIAS',(-.28,.27,.133),.032,ink,parent=root)
for i,word in enumerate(['Recordar','Descobrir','Sentir','Partilhar','Imaginar']):
    y=.18-i*.105
    text('Opcao_'+str(i),word,(-.28,y,.133),.029,ink,parent=root)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.026,depth=.004)
    o=move(bpy.context.object); o.name='Sensor_pressao_'+str(i+1)
    o.parent=root; o.location=(.42,y,.132); o.data.materials.append(black)
    o['tipo']='Sensor conceptual, sem ligação física'; o['canal']=i+1
    pts=[(.42+.033*math.cos(a*math.tau/64),y+.033*math.sin(a*math.tau/64),.136) for a in range(65)]
    line('Indicador_sensor_'+str(i+1),pts,.002,cyan if i==SENSOR_ATIVO else white,root)
text('Texto_pagina_direita','ESCUTA\n\nCada toque desperta\numa nova memória.',
     (.26,.25,.134),.031,ink,parent=root)
 
# Cubo vazio por dentro: arestas e planos transparentes, sem bloco sólido.
for axis in range(3):
    others=[i for i in range(3) if i!=axis]
    for s1 in (-1,1):
        for s2 in (-1,1):
            a=[cx,cy,cz]; b=a.copy(); a[axis]-=half; b[axis]+=half
            for idx,sign in zip(others,(s1,s2)):
                a[idx]+=sign*half; b[idx]+=sign*half
            line('Aresta_cubo',[a,b],.004,cyan)
panel('Tela_transparente_word_cloud',(cx,cy-half-.002,cz),CUBO_LADO,CUBO_LADO,screen)
for x in (cx-half,cx+half):
    o=panel('Lateral_transparente',(0,0,0),CUBO_LADO,CUBO_LADO,screen)
    o.rotation_euler.z=math.pi/2; o.location=(x,cy,cz)
 
# Sem vídeo não cria painel opaco de substituição.
if VIDEO_PATH:
    path=Path(bpy.path.abspath(VIDEO_PATH))
    if not path.is_file(): raise FileNotFoundError('Vídeo inexistente: '+str(path))
    mat=glow('Video_interior',SKY_BLUE,.9,.65)
    image=bpy.data.images.load(str(path),check_existing=True); image.source='MOVIE'
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=image
    tex.image_user.use_auto_refresh=True; tex.image_user.use_cyclic=True
    tex.image_user.frame_start=1; tex.image_user.frame_duration=max(1,image.frame_duration)
    em=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
    mat.node_tree.links.new(tex.outputs['Color'],em.inputs[0])
    panel('Video_interior_cubo',(cx,cy+half-.03,cz),CUBO_LADO*.92,CUBO_LADO*.92,mat)
layout=[(0,.22,.071),(-.15,.12,.039),(.13,.10,.045),(0,-.01,.077),
        (-.18,-.12,.036),(.15,-.13,.037),(0,-.23,.046),(-.19,-.30,.027),(.21,.30,.033),(.16,-.31,.026)]
for i,(word,(dx,dz,size)) in enumerate(zip(PALAVRAS,layout)):
    text('WordCloud_'+str(i),word,(cx+dx,cy-half-.012,cz+dz),size,
         white if i%3 else cyan,(math.pi/2,0,0))
if MOSTRAR_FLUXOS:
    bpy.context.view_layer.update()
    start=root.matrix_world @ Vector((.59,.10,.14))
    end=Vector((cx-half,cy,cz-.20))
    for j in range(12):
        pts=[]
        for k in range(65):
            t=k/64; v=start.lerp(end,t); fade=math.sin(math.pi*t)
            v.y+=.045*math.sin(t*8+j)*fade
            v.z+=.06*math.sin(t*9+j*.45)*fade
            pts.append(tuple(v))
        line('Fluxo_'+str(j),pts,.0018,cyan if j%3 else purple)
 
def light(name,loc,energy,color,size=1,target=None,kind='AREA'):
    d=bpy.data.lights.new(name,kind); d.energy=energy; d.color=color
    if kind=='AREA': d.shape='DISK'; d.size=size
    else: d.shadow_soft_size=size
    o=bpy.data.objects.new(name,d); collection.objects.link(o); o.location=loc
    if target: o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('Luz_livro',(-2,-2,4),450,(1,.75,.48),3,(book_x,book_y,1))
light('Luz_ambiente',(2,-1,4.2),350,(.65,.8,1),4,(0,1,1))
light('Interior_sky_blue',(cx,cy,cz),18,(.53,.81,.92),.2,kind='POINT')
light('Luz_fundo',(0,3.5,3.6),220,(1,.7,.45),2,(0,4.8,2))
d=bpy.data.cameras.new('Camera_instalacao'); cam=bpy.data.objects.new('Camera_instalacao',d)
collection.objects.link(cam); cam.location=(3.4,-6.5,3)
cam.rotation_euler=(Vector((-.35,.7,1.35))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=48; scene.camera=cam; scene.frame_set(1)
if OUTPUT_BLEND: bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUTPUT_BLEND))
if RENDER_IMAGE:
    scene.render.filepath=bpy.path.abspath(RENDER_IMAGE)
    scene.render.image_settings.file_format='PNG'
    bpy.ops.render.render(write_still=True)
print('Instalação recriada sem bloco branco. Numpad 0: câmara. F12: render.')
