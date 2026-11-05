"""Vídeo POV procedural da instalação. Blender, render Cycles.
ATENÇÃO: remove todos os objetos da cena ativa.
A proximidade e a pressão são eventos encenados, não leituras de hardware.
Executa o script e usa Ctrl+F12 para renderizar a animação.
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector
 
# CONFIGURAÇÃO
RENDERIZAR_AGORA = False
VIDEO_OUTPUT = str(Path.home() / 'instalacao_pov.mp4')
OUTPUT_BLEND = r''
FPS = 25
FRAME_FINAL = 450
AMOSTRAS = 32
RESOLUCAO = (1280, 720)
PALAVRA_DESTACADA = 'EMOÇÃO'
PALAVRAS = ['MEMÓRIA','PARTILHA','FUTURO','CULTURA','EMOÇÃO',
            'HISTÓRIA','IDENTIDADE','CONEXÃO','VOZ','DESCOBERTA']
FRAME_SENSOR = 125
FRAME_PRESSAO = 270
FRAME_DESTAQUE = 300
CUBO_LADO = .90
POSTE_ALTURA = 1.57
FOLGA_LIVRO_CUBO = .08
SKY_BLUE = (.235,.617,.831,1)
 
scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
for obj in list(scene.objects):
    if len(obj.users_scene)>1: raise RuntimeError('Objeto partilhado com outra cena: '+obj.name)
for obj in list(scene.objects): bpy.data.objects.remove(obj,do_unlink=True)
col=bpy.data.collections.new('Instalacao_POV'); scene.collection.children.link(col)
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'; scene.cycles.samples=AMOSTRAS
scene.cycles.use_denoising=True
scene.render.resolution_x,scene.render.resolution_y=RESOLUCAO
scene.render.resolution_percentage=100
scene.render.fps=FPS; scene.frame_start=1; scene.frame_end=FRAME_FINAL
scene.world=bpy.data.worlds.new('Ambiente'); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.035,.05,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.30
try: scene.view_settings.view_transform='AgX'
except TypeError: pass
 
def move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    return o
 
def solid(name,color,rough=.8,metal=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=color
    n.inputs['Roughness'].default_value=rough; n.inputs['Metallic'].default_value=metal
    return m
 
def glow(name,color,strength=2,visibility=1):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes; n.clear()
    out=n.new('ShaderNodeOutputMaterial'); em=n.new('ShaderNodeEmission')
    em.inputs[0].default_value=color; em.inputs[1].default_value=strength
    if visibility<1:
        tr=n.new('ShaderNodeBsdfTransparent'); mix=n.new('ShaderNodeMixShader')
        mix.inputs[0].default_value=visibility
        m.node_tree.links.new(tr.outputs[0],mix.inputs[1]); m.node_tree.links.new(em.outputs[0],mix.inputs[2])
        m.node_tree.links.new(mix.outputs[0],out.inputs[0])
    else: m.node_tree.links.new(em.outputs[0],out.inputs[0])
    return m,em
 
black=solid('Preto_mate',(.009,.009,.011,1),.95)
paper=solid('Papel',(.69,.53,.32,1)); cover=solid('Capa',(.12,.045,.018,1))
ink=solid('Tinta',(.035,.02,.01,1)); floor=solid('Pavimento',(.04,.05,.06,1),.28)
wall=solid('Parede',(.055,.065,.075,1))
pcb=solid('PCB',(.015,.09,.24,1),.5); metal=solid('Aluminio',(.45,.49,.53,1),.28,.85)
skin=solid('Mao_estilizada',(.46,.25,.14,1),.65)
cyan,_=glow('Sky_blue',SKY_BLUE,2)
white,_=glow('Palavras',(.55,.85,1,1),1.5)
screen,_=glow('Tela',SKY_BLUE,.6,.035)
active,active_node=glow('Sensor_proximidade_estado',(.05,.8,1,1),1)
buttonmat,button_node=glow('Botao_estado',(.08,.3,.45,1),.5)
 
# Construção de objetos.
def box(name,loc,size,mat,parent=None,bevel=.006):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=move(bpy.context.object); o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.parent=parent; o.location=loc; o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Arestas','BEVEL'); b.width=bevel; b.segments=3
    return o
 
def cylinder(name,loc,radius,depth,mat,parent=None,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth)
    o=move(bpy.context.object); o.name=name; o.parent=parent; o.location=loc
    o.rotation_euler=rotation; o.data.materials.append(mat)
    return o
 
def line(name,pts,radius,mat,parent=None):
    d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'; d.bevel_depth=radius; d.bevel_resolution=3
    s=d.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,d); col.objects.link(o); o.parent=parent; d.materials.append(mat)
    return o
 
def text(name,body,loc,size,mat,parent=None,rotation=(0,0,0)):
    d=bpy.data.curves.new(name,'FONT'); d.body=body; d.size=size
    d.align_x='CENTER'; d.align_y='CENTER'; d.extrude=.0002
    o=bpy.data.objects.new(name,d); col.objects.link(o)
    o.parent=parent; o.location=loc; o.rotation_euler=rotation; d.materials.append(mat)
    return o
 
def panel(name,loc,w,h,mat):
    x,y,z=loc; mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[],[(0,1,2,3)])
    mesh.update(); o=bpy.data.objects.new(name,mesh); col.objects.link(o); mesh.materials.append(mat)
    return o
 
box('Pavimento',(0,0,-.08),(12,14,.16),floor)
box('Parede_fundo',(0,5,2.3),(12,.16,4.6),wall)
for x in (-4,-2,2,4): box('Quadro_escuro',(x,4.88,2.2),(1,.04,1.4),black)
cx,cy=.55,.7; half=CUBO_LADO/2; cz=POSTE_ALTURA+half
box('Poste_PRETO_MATE',(cx,cy,POSTE_ALTURA/2),(CUBO_LADO,CUBO_LADO,POSTE_ALTURA),black)
bx=cx-half-FOLGA_LIVRO_CUBO-.62; by=cy
box('Podio_PRETO_MATE',(bx,by,.58),(.48,.48,1.16),black)
root=bpy.data.objects.new('Livro',None); col.objects.link(root)
root.location=(bx,by,1.2); root.rotation_euler.x=math.radians(20)
box('Apoio_PRETO_MATE',(0,0,0),(1.24,.85,.045),black,root)
box('Capa',(0,0,.035),(1.18,.79,.04),cover,root)
for s in (-1,1): box('Paginas',(s*.29,0,.09),(.565,.74,.075),paper,root)
line('Vinco',[(0,-.37,.135),(0,.37,.135)],.005,cover,root)
text('Titulo','UM LIVRO DE MEMÓRIAS',(-.28,.28,.133),.031,ink,root)
buttons=[]
for i,label in enumerate(['Recordar','Descobrir','Sentir','Partilhar','Imaginar']):
    y=.18-i*.105
    text('Opcao',label,(-.28,y,.133),.029,ink,root)
    b=cylinder('Sensor_pressao_'+str(i+1),(.42,y,.132),.026,.004,black,root); buttons.append(b)
    pts=[(.42+.033*math.cos(a*math.tau/64),y+.033*math.sin(a*math.tau/64),.136) for a in range(65)]
    line('Anel_botao',pts,.002,buttonmat if i==2 else white,root)
text('Pagina_direita','ESCUTA\n\nToca para descobrir\numa nova emoção.',(.25,.26,.134),.030,ink,root)
 
# Sensor elevado na margem superior do livro.
sensor=bpy.data.objects.new('Sensor_ultrassonico',None); col.objects.link(sensor)
sensor.parent=root; sensor.location=(0,.32,.248)
sensor['funcional']=False
box('PCB',(0,0,0),(.10,.004,.045),pcb,sensor,.001)
for x in (-.027,.027):
    cylinder('Transdutor',(x,-.012,0),.018,.020,metal,sensor,(math.pi/2,0,0))
    cylinder('Membrana',(x,-.0225,0),.0145,.0015,black,sensor,(math.pi/2,0,0))
cylinder('LED_sensor',(.041,-.003,-.012),.002,.002,active,sensor,(math.pi/2,0,0))
box('Suporte_sensor',(0,.365,.144),(.018,.018,.208),black,root,.002)
box('Braco_sensor',(0,.345,.248),(.018,.058,.014),black,root,.002)
line('Cabo_sensor',[(0,.335,.23),(.04,.40,.21),(.06,.42,-.03)],.002,black,root)
for frame,power in [(1,1),(FRAME_SENSOR-1,1),(FRAME_SENSOR+5,5),(FRAME_FINAL,5)]:
    active_node.inputs[1].default_value=power; active_node.inputs[1].keyframe_insert('default_value',frame=frame)
 
# Cubo transparente e word cloud.
for axis in range(3):
    other=[i for i in range(3) if i!=axis]
    for s1 in (-1,1):
        for s2 in (-1,1):
            a=[cx,cy,cz]; b=a.copy(); a[axis]-=half; b[axis]+=half
            for idx,s in zip(other,(s1,s2)): a[idx]+=s*half; b[idx]+=s*half
            line('Aresta_cubo',[a,b],.004,cyan)
panel('Tela_frontal',(cx,cy-half-.002,cz),.90,.90,screen)
for x in (cx-half,cx+half):
    o=panel('Tela_lateral',(0,0,0),.9,.9,screen); o.rotation_euler.z=math.pi/2; o.location=(x,cy,cz)
layout=[(0,.28,.066),(-.19,.18,.035),(.15,.16,.042),(0,.055,.065),
        (0,-.07,.040),(.17,-.18,.032),(0,-.28,.038),(-.19,-.18,.027),(.22,.32,.032),(.16,-.35,.025)]
cloud=[]
for i,(word,(dx,dz,size)) in enumerate(zip(PALAVRAS,layout)):
    base=Vector((cx+dx,cy-half-.012,cz+dz))
    o=text('WordCloud_'+word,word,base,size,white,rotation=(math.pi/2,0,0)); cloud.append(o)
    # Variação tipográfica até à aproximação; depois congela exatamente.
    for frame in [1,25,50,75,100,FRAME_SENSOR]:
        phase=frame*.065+i*.8
        o.location=base+Vector((.012*math.sin(phase),0,.01*math.cos(phase)))
        scale=1+.12*math.sin(phase)
        o.scale=(scale,scale,scale)
        o.keyframe_insert('location',frame=frame); o.keyframe_insert('scale',frame=frame)
    frozen_loc=o.location.copy(); frozen_scale=o.scale.copy()
    for frame in [FRAME_PRESSAO,FRAME_FINAL]:
        o.location=frozen_loc; o.scale=frozen_scale
        o.keyframe_insert('location',frame=frame); o.keyframe_insert('scale',frame=frame)
    if word==PALAVRA_DESTACADA:
        # Liberta o centro para a palavra escolhida e aumenta a sua escala.
        o.location=(cx,cy-half-.018,cz-.07); o.scale=(2.0,2.0,2.0)
        o.keyframe_insert('location',frame=FRAME_DESTAQUE); o.keyframe_insert('scale',frame=FRAME_DESTAQUE)
        o.keyframe_insert('location',frame=FRAME_FINAL); o.keyframe_insert('scale',frame=FRAME_FINAL)
        o.data.materials.clear(); o.data.materials.append(cyan)
 
# Pressão visível no terceiro botão.
b=buttons[2]
for f,z in [(1,.132),(FRAME_PRESSAO-6,.132),(FRAME_PRESSAO,.128),(FRAME_PRESSAO+8,.128),
            (FRAME_PRESSAO+16,.132),(FRAME_FINAL,.132)]:
    b.location.z=z; b.keyframe_insert('location',frame=f)
for f,power in [(1,.5),(FRAME_PRESSAO-1,.5),(FRAME_PRESSAO+3,4),(FRAME_FINAL,4)]:
    button_node.inputs[1].default_value=power; button_node.inputs[1].keyframe_insert('default_value',frame=f)
 
# Mão estilizada: apenas mão e dedo do visitante, sem corpo na cena.
hand=bpy.data.objects.new('Mao_POV',None); col.objects.link(hand); hand.parent=root
# A ponta do indicador fica na origem local da mão.
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1)
o=move(bpy.context.object); o.name='Indicador'; o.parent=hand
# Dedo estendido ao longo do eixo Y do livro.
o.location=(0,-.047,.006); o.scale=(.009,.056,.009); o.data.materials.append(skin)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1)
o=move(bpy.context.object); o.name='Palma'; o.parent=hand
o.location=(0,-.145,.014); o.scale=(.035,.057,.019); o.data.materials.append(skin)
for i in range(3):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=12,radius=1)
    o=move(bpy.context.object); o.name='Dedos_recolhidos'; o.parent=hand
    o.location=(-.019+i*.018,-.103,.012); o.scale=(.009,.024,.012); o.data.materials.append(skin)
# Entrada e saída da mão por baixo do enquadramento.
for f,loc,scale in [(1,(.42,-.70,.30),0),(220,(.42,-.70,.30),0),
                    (230,(.42,-.55,.24),1),(255,(.42,-.04,.19),1),
                    (FRAME_PRESSAO,(.42,-.03,.137),1),(278,(.42,-.03,.137),1),
                    (292,(.42,-.12,.25),1),(315,(.42,-.70,.30),1),
                    (325,(.42,-.70,.30),0),(FRAME_FINAL,(.42,-.70,.30),0)]:
    hand.location=loc; hand.scale=(scale,)*3
    hand.keyframe_insert('location',frame=f); hand.keyframe_insert('scale',frame=f)
 
if MOSTRAR_FLUXOS:
    bpy.context.view_layer.update()
    start=root.matrix_world @ Vector((.59,.10,.14)); end=Vector((cx-half,cy,cz-.20))
    for j in range(9):
        pts=[]
        for k in range(49):
            t=k/48; v=start.lerp(end,t)
            v.y+=.035*math.sin(t*8+j)*math.sin(math.pi*t)
            v.z+=.045*math.sin(t*7+j)*math.sin(math.pi*t); pts.append(tuple(v))
        line('Fluxo',pts,.0015,cyan)
 
def light(name,loc,power,color,target=None,kind='AREA'):
    d=bpy.data.lights.new(name,kind); d.energy=power; d.color=color
    if kind=='AREA': d.size=3
    else: d.shadow_soft_size=.15
    o=bpy.data.objects.new(name,d); col.objects.link(o); o.location=loc
    if target: o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('Luz_livro',(-2,-2,4),450,(1,.78,.55),(bx,by,1))
light('Luz_geral',(2,-1,4),350,(.65,.8,1),(0,1,1))
light('Luz_cubo',(cx,cy,cz),16,(.53,.81,.92),kind='POINT')
 
# Câmara POV: percurso de chegada e mudanças de olhar.
bpy.context.view_layer.update()
book_target=root.matrix_world @ Vector((0,0,.135))
button_target=root.matrix_world @ Vector((.42,-.03,.132))
sensor_target=sensor.matrix_world.translation.copy()
cam_data=bpy.data.cameras.new('Camera_POV'); cam=bpy.data.objects.new('Camera_POV',cam_data)
col.objects.link(cam); scene.camera=cam
cam.data.lens=25; cam.data.clip_start=.03
cam.rotation_mode='QUATERNION'
near=(bx,-.22,1.72)
poses=[(1,(-.9,-4.3,1.68),(0,.7,1.6)),
       (85,(bx,-1.1,1.70),(0,.7,1.65)),
       (FRAME_SENSOR,near,sensor_target),
       (150,near,(cx,cy,cz)),(195,near,(cx,cy,cz)),
       (225,near,book_target),(255,near,button_target),
       (285,near,button_target),(330,near,(cx,cy,cz)),
       (FRAME_FINAL,near,(cx,cy,cz))]
previous=None
for frame,loc,target in poses:
    cam.location=loc
    q=(Vector(target)-cam.location).to_track_quat('-Z','Y')
    if previous is not None and previous.dot(q)<0: q.negate()
    cam.rotation_quaternion=q; previous=q.copy()
    cam.keyframe_insert('location',frame=frame)
    cam.keyframe_insert('rotation_quaternion',frame=frame)
# Marcadores na timeline.
for name,frame in [('Chegada',1),('Sensor: congelar palavras',FRAME_SENSOR),
                   ('Olhar cubo parado',150),('Olhar livro',225),
                   ('Pressionar Sentir',FRAME_PRESSAO),('Destacar EMOÇÃO',FRAME_DESTAQUE),
                   ('Olhar cubo final',330)]:
    marker=scene.timeline_markers.new(name); marker.frame=frame
# Interpolação linear evita overshoot, mantendo intervalos de imobilidade.
# Compatibilidade com Actions antigas e Actions com slots.
def fcurves(action):
    try: return list(action.fcurves)
    except AttributeError:
        curves=[]
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    try:
                        bag=strip.channelbag(slot)
                        if bag: curves.extend(bag.fcurves)
                    except (AttributeError,RuntimeError): pass
        return curves
for action in bpy.data.actions:
    for fc in fcurves(action):
        for key in fc.keyframe_points: key.interpolation='LINEAR'
 
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'
scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath=VIDEO_OUTPUT
scene.render.use_file_extension=True
scene.frame_set(1)
if OUTPUT_BLEND: bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUTPUT_BLEND))
if RENDERIZAR_AGORA:
    Path(bpy.path.abspath(VIDEO_OUTPUT)).parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.render.render(animation=True)
print('POV preparado: 450 fotogramas, 18 segundos a 25 fps. Ctrl+F12: renderizar vídeo.')
