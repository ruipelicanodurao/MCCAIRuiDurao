"""POV com word cloud densa e duas interações. Blender.
ATENÇÃO: elimina os objetos da cena ativa. Eventos encenados, sem hardware.
Executar Run Script; Ctrl+F12 renderiza o MP4.
"""
import bpy
import math
import random
from pathlib import Path
from mathutils import Vector
 
MOSTRAR_FLUXOS = False
RENDERIZAR_AGORA = False
VIDEO_OUTPUT = r'C:\Users\rui_durao\Downloads\Mestrado_IADE\MCCAIRuiDurao\1stSEMESTER\PROJECT1\instalacao_pov.mp4'
OUTPUT_BLEND = r''
FPS = 25
FRAME_FINAL = 650
AMOSTRAS = 32
RESOLUCAO = (1280,720)
FRAME_SENSOR = 150
PRESSAO_1 = 290
DESTAQUE_1 = 315
PRESSAO_2 = 490
DESTAQUE_2 = 515
PALAVRA_1 = 'EMOÇÃO'
PALAVRA_2 = 'MEMÓRIA'
BOTAO_1 = 2  # Índice 0..4: Sentir
BOTAO_2 = 0  # Índice 0..4: Recordar
CUBO_LADO = .90
POSTE_ALTURA = 1.57
FOLGA_LIVRO_CUBO = .08
SKY_BLUE = (.235,.617,.831,1)
PALAVRAS = ['MEMÓRIA','PARTILHA','FUTURO','CULTURA','EMOÇÃO','HISTÓRIA',
 'IDENTIDADE','CONEXÃO','VOZ','DESCOBERTA','TEMPO','ENCONTRO',
 'SAUDADE','AFETO','PRESENÇA','ESCUTA','ORIGEM','COMUNIDADE',
 'SONHO','VIDA','OLHAR','SENTIR','RECORDAR','IMAGINAR',
 'DIÁLOGO','HERANÇA','VIAGEM','ESPERANÇA','RAÍZES','MUNDO',
 'EXPERIÊNCIA','PESSOAS','SABER','ARTE','IDEIAS','PERTENÇA']
if len(PALAVRAS)>36: raise ValueError('O layout desta versão admite até 36 palavras.')
if PALAVRA_1 not in PALAVRAS or PALAVRA_2 not in PALAVRAS:
    raise ValueError('As palavras destacadas têm de existir na lista.')
if PALAVRA_1 == PALAVRA_2: raise ValueError('Escolhe duas palavras distintas.')
 
scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
for o in list(scene.objects):
    if len(o.users_scene)>1: raise RuntimeError('Objeto partilhado com outra cena: '+o.name)
for o in list(scene.objects): bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections.new('Instalacao_POV_Duas_Interacoes'); scene.collection.children.link(col)
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'; scene.cycles.samples=AMOSTRAS; scene.cycles.use_denoising=True
scene.render.resolution_x,scene.render.resolution_y=RESOLUCAO
scene.render.resolution_percentage=100; scene.render.fps=FPS
scene.frame_start=1; scene.frame_end=FRAME_FINAL
scene.world=bpy.data.worlds.new('Ambiente'); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.035,.05,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.30
try: scene.view_settings.view_transform='AgX'
except TypeError: pass
 
def move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); return o
 
def solid(name,color,rough=.8,metal=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF'); n.inputs['Base Color'].default_value=color
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
wall=solid('Parede',(.055,.065,.075,1)); pcb=solid('PCB',(.015,.09,.24,1),.5)
metal=solid('Aluminio',(.45,.49,.53,1),.28,.85); skin=solid('Mao',(.46,.25,.14,1),.65)
cyan,_=glow('Sky_blue',SKY_BLUE,2); white,_=glow('Palavras',(.55,.85,1,1),1.5)
screen,_=glow('Tela',SKY_BLUE,.6,.035)
active,active_node=glow('Estado_sensor',(.05,.8,1,1),1)
 
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
    o.rotation_euler=rotation; o.data.materials.append(mat); return o
 
def line(name,pts,radius,mat,parent=None):
    d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'; d.bevel_depth=radius; d.bevel_resolution=3
    s=d.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,d); col.objects.link(o); o.parent=parent; d.materials.append(mat); return o
 
def text(name,body,loc,size,mat,parent=None,rotation=(0,0,0)):
    d=bpy.data.curves.new(name,'FONT'); d.body=body; d.size=size
    d.align_x='CENTER'; d.align_y='CENTER'; d.extrude=.0002
    o=bpy.data.objects.new(name,d); col.objects.link(o); o.parent=parent
    o.location=loc; o.rotation_euler=rotation; d.materials.append(mat); return o
 
def panel(name,loc,w,h,mat):
    x,y,z=loc; mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[],[(0,1,2,3)])
    mesh.update(); o=bpy.data.objects.new(name,mesh); col.objects.link(o); mesh.materials.append(mat); return o
 
def key_transform(o,frame,loc,scale=1):
    o.location=loc; o.scale=(scale,)*3
    o.keyframe_insert('location',frame=frame); o.keyframe_insert('scale',frame=frame)
 
box('Pavimento',(0,0,-.08),(12,14,.16),floor)
box('Parede_fundo',(0,5,2.3),(12,.16,4.6),wall)
for x in (-4,-2,2,4): box('Quadro',(x,4.88,2.2),(1,.04,1.4),black)
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
buttons=[]; button_nodes=[]
for i,label in enumerate(['Recordar','Descobrir','Sentir','Partilhar','Imaginar']):
    y=.18-i*.105
    text('Opcao_'+label,label,(-.28,y,.133),.029,ink,root)
    buttons.append(cylinder('Sensor_pressao_'+str(i+1),(.42,y,.132),.026,.004,black,root))
    mat,node=glow('Estado_botao_'+str(i),(.08,.3,.45,1),.5); button_nodes.append(node)
    pts=[(.42+.033*math.cos(a*math.tau/64),y+.033*math.sin(a*math.tau/64),.136) for a in range(65)]
    line('Anel_botao',pts,.002,mat,root)
text('Pagina_direita','ESCUTA\n\nCada toque revela\numa nova palavra.',(.25,.26,.134),.030,ink,root)
sensor=bpy.data.objects.new('Sensor_ultrassonico',None); col.objects.link(sensor)
sensor.parent=root; sensor.location=(0,.32,.248); sensor['funcional']=False
box('PCB',(0,0,0),(.10,.004,.045),pcb,sensor,.001)
for x in (-.027,.027):
    cylinder('Transdutor',(x,-.012,0),.018,.020,metal,sensor,(math.pi/2,0,0))
    cylinder('Membrana',(x,-.0225,0),.0145,.0015,black,sensor,(math.pi/2,0,0))
cylinder('LED_sensor',(.041,-.003,-.012),.002,.002,active,sensor,(math.pi/2,0,0))
box('Suporte_sensor',(0,.365,.144),(.018,.018,.208),black,root,.002)
box('Braco_sensor',(0,.345,.248),(.018,.058,.014),black,root,.002)
line('Cabo',[(0,.335,.23),(.04,.40,.21),(.06,.42,-.03)],.002,black,root)
for f,p in [(1,1),(FRAME_SENSOR-1,1),(FRAME_SENSOR+5,5),(FRAME_FINAL,5)]:
    active_node.inputs[1].default_value=p; active_node.inputs[1].keyframe_insert('default_value',frame=f)
for axis in range(3):
    other=[i for i in range(3) if i!=axis]
    for s1 in (-1,1):
        for s2 in (-1,1):
            a=[cx,cy,cz]; b=a.copy(); a[axis]-=half; b[axis]+=half
            for idx,s in zip(other,(s1,s2)): a[idx]+=s*half; b[idx]+=s*half
            line('Aresta_cubo',[a,b],.004,cyan)
panel('Tela_frontal',(cx,cy-half-.002,cz),.9,.9,screen)
for x in (cx-half,cx+half):
    o=panel('Tela_lateral',(0,0,0),.9,.9,screen); o.rotation_euler.z=math.pi/2; o.location=(x,cy,cz)
 
# 36 palavras, ocupando uma grelha 6x6; comprimentos ajustados automaticamente.
cloud=[]; widths=[]; heights=[]
for word in PALAVRAS:
    o=text('WordCloud_'+word,word,(cx,cy-half-.012,cz),.05,white,rotation=(math.pi/2,0,0))
    cloud.append(o)
bpy.context.view_layer.update()
for o in cloud:
    widths.append(max(o.dimensions.x,.001)); heights.append(max(o.dimensions.z,.001))
slots=[(-.34+c*.136,.35-r*.14) for r in range(6) for c in range(6)]
# Para os destaques, deixa uma faixa central vazia, evitando sobreposições.
focus_slots=[(-.34+c*.136,z) for z in [.35,.27,.19,-.19,-.27,-.35] for c in range(6)]
def normal_state(seed):
    rng=random.Random(seed); indices=list(range(36)); rng.shuffle(indices)
    state=[]
    for i in range(len(cloud)):
        x,z=slots[indices[i]]
        scale=min(.122/widths[i],.065/heights[i]) * rng.uniform(.72,1.0)
        state.append(((cx+x,cy-half-.012,cz+z),scale))
    return state
 
def focus_state(word):
    selected=PALAVRAS.index(word); state=[]; slot=0
    for i in range(len(cloud)):
        if i==selected:
            state.append(((cx,cy-half-.018,cz),min(.70/widths[i],.12/heights[i])))
        else:
            x,z=focus_slots[slot]; slot+=1
            state.append(((cx+x,cy-half-.012,cz+z),min(.122/widths[i],.049/heights[i])*.9))
    return state
 
def apply_state(frame,state):
    for o,(loc,scale) in zip(cloud,state): key_transform(o,frame,loc,scale)
# Mudanças discretas a cada FPS fotogramas = exatamente 1 segundo.
frozen=None
for n,f in enumerate(range(1,FRAME_SENSOR,FPS)):
    frozen=normal_state(200+n); apply_state(f,frozen)
apply_state(FRAME_SENSOR,frozen)
apply_state(PRESSAO_1,frozen)
state1=focus_state(PALAVRA_1); state2=focus_state(PALAVRA_2)
apply_state(DESTAQUE_1,state1); apply_state(PRESSAO_2,state1)
apply_state(DESTAQUE_2,state2); apply_state(FRAME_FINAL,state2)
 
# Duas pressões distintas, com descida e retorno dos botões.
for idx,frame in [(BOTAO_1,PRESSAO_1),(BOTAO_2,PRESSAO_2)]:
    o=buttons[idx]
    for f,z in [(1,.132),(frame-6,.132),(frame,.128),(frame+8,.128),(frame+16,.132),(FRAME_FINAL,.132)]:
        o.location.z=z; o.keyframe_insert('location',frame=f)
    node=button_nodes[idx]
    for f,p in [(1,.5),(frame-1,.5),(frame+3,4),(frame+30,4),(frame+45,.5),(FRAME_FINAL,.5)]:
        node.inputs[1].default_value=p; node.inputs[1].keyframe_insert('default_value',frame=f)
 
# Mão POV estilizada, sem personagem completa.
hand=bpy.data.objects.new('Mao_POV',None); col.objects.link(hand); hand.parent=root
for name,loc,scale in [('Indicador',(0,-.047,.006),(.009,.056,.009)),
                        ('Palma',(0,-.145,.014),(.035,.057,.019))]+[
                        ('Dedo',(-.019+i*.018,-.103,.012),(.009,.024,.012)) for i in range(3)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1)
    o=move(bpy.context.object); o.name=name; o.parent=hand; o.location=loc; o.scale=scale
    o.data.materials.append(skin)
key_transform(hand,1,(.42,-.70,.30),0)
for idx,press in [(BOTAO_1,PRESSAO_1),(BOTAO_2,PRESSAO_2)]:
    y=.18-idx*.105
    for f,loc,s in [(press-60,(.42,-.70,.30),0),(press-50,(.42,-.55,.24),1),
                     (press-15,(.42,y,.19),1),(press,(.42,y,.137),1),
                     (press+8,(.42,y,.137),1),(press+22,(.42,y-.09,.25),1),
                     (press+35,(.42,-.70,.30),1),(press+45,(.42,-.70,.30),0)]:
        key_transform(hand,f,loc,s)
key_transform(hand,FRAME_FINAL,(.42,-.70,.30),0)
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
bpy.context.view_layer.update()
book_target=root.matrix_world @ Vector((0,0,.135))
target1=root.matrix_world @ buttons[BOTAO_1].location
target2=root.matrix_world @ buttons[BOTAO_2].location
sensor_target=sensor.matrix_world.translation.copy()
d=bpy.data.cameras.new('Camera_POV'); cam=bpy.data.objects.new('Camera_POV',d)
col.objects.link(cam); scene.camera=cam; cam.data.lens=25; cam.data.clip_start=.03
cam.rotation_mode='QUATERNION'; near=(bx,-.22,1.72); cube_target=(cx,cy,cz)
poses=[(1,(-.9,-4.3,1.68),(0,.7,1.6)),(100,(bx,-1.1,1.70),(0,.7,1.65)),
 (FRAME_SENSOR,near,sensor_target),(180,near,cube_target),(220,near,cube_target),
 (250,near,book_target),(275,near,target1),(305,near,target1),
 (345,near,cube_target),(410,near,cube_target),
 (450,near,book_target),(475,near,target2),(505,near,target2),
 (545,near,cube_target),(FRAME_FINAL,near,cube_target)]
previous=None
for f,loc,target in poses:
    cam.location=loc; q=(Vector(target)-cam.location).to_track_quat('-Z','Y')
    if previous is not None and previous.dot(q)<0: q.negate()
    cam.rotation_quaternion=q; previous=q.copy()
    cam.keyframe_insert('location',frame=f); cam.keyframe_insert('rotation_quaternion',frame=f)
scene.timeline_markers.clear()
for name,f in [('Chegada: cloud muda a cada segundo',1),('Sensor: cloud congela',FRAME_SENSOR),
 ('Mostrar cloud parada',180),('Olhar livro 1',250),('Botão Sentir',PRESSAO_1),
 ('EMOÇÃO maior',DESTAQUE_1),('Mostrar cubo 1',345),('Olhar livro 2',450),
 ('Botão Recordar',PRESSAO_2),('EMOÇÃO pequena; MEMÓRIA maior',DESTAQUE_2),('Mostrar cubo 2',545)]:
    scene.timeline_markers.new(name,frame=f)
 
# FCurves: suporta Actions com e sem slots.
def curves(action):
    try: return list(action.fcurves)
    except AttributeError:
        result=[]
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    try:
                        bag=strip.channelbag(slot)
                        if bag: result.extend(bag.fcurves)
                    except (AttributeError,RuntimeError): pass
        return result
# Altera apenas as animações desta instalação.
ids=list(col.objects)+[active_node.id_data]+[n.id_data for n in button_nodes]
for owner in ids:
    ad=owner.animation_data
    if ad and ad.action:
        for fc in curves(ad.action):
            for key in fc.keyframe_points: key.interpolation='LINEAR'
# Antes do sensor, cada estado mantém-se fixo 1 s e muda num salto.
# Depois do sensor, fica parado até às transições provocadas pelos botões.
for o in cloud:
    for fc in curves(o.animation_data.action):
        for key in fc.keyframe_points:
            if key.co.x < FRAME_SENSOR: key.interpolation='CONSTANT'
 
# Mantém a configuração de vídeo que funcionou na tua versão.
if hasattr(scene.render.image_settings,'media_type'):
    scene.render.image_settings.media_type='VIDEO'
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'
scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath=VIDEO_OUTPUT; scene.render.use_file_extension=True
Path(bpy.path.abspath(VIDEO_OUTPUT)).parent.mkdir(parents=True,exist_ok=True)
scene.frame_set(1)
if OUTPUT_BLEND: bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUTPUT_BLEND))
if RENDERIZAR_AGORA: bpy.ops.render.render(animation=True)
print('POV pronto: 36 palavras, mudanças de 1 s, duas pressões; 26 segundos a 25 fps.')
