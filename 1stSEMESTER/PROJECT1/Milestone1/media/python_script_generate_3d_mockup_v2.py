import bpy
import math
from pathlib import Path
from mathutils import Vector
 
# CONFIGURAÇÃO — medidas aproximadas em metros
VIDEO_PATH = r""
OUTPUT_BLEND = r""
CUBO_LADO = 0.90
POSTE_ALTURA = 1.57
FOLGA_LIVRO_CUBO = 0.08
PALAVRAS = ['MEMÓRIA', 'PARTILHA', 'FUTURO', 'CULTURA', 'EMOÇÃO',
            'HISTÓRIA', 'IDENTIDADE', 'CONEXÃO', 'VOZ', 'DESCOBERTA']
SENSOR_ATIVO = 2
NAME = 'Instalacao_Procedural'
 
old = bpy.data.collections.get(NAME)
if old:
    for obj in list(old.all_objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(NAME)
bpy.context.scene.collection.children.link(col)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.fps = 25
scene.frame_end = 250
world = bpy.data.worlds.new('Ambiente_instalacao')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.025,0.035,0.05,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.3
scene.world = world
 
def material(name,color,roughness=0.8,emission=0,transparent=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    nodes=m.node_tree.nodes; nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial')
    if emission:
        shader=nodes.new('ShaderNodeEmission')
        shader.inputs[0].default_value=color
        shader.inputs[1].default_value=emission
    else:
        shader=nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Base Color'].default_value=color
        shader.inputs['Roughness'].default_value=roughness
    if transparent:
        tr=nodes.new('ShaderNodeBsdfTransparent')
        mix=nodes.new('ShaderNodeMixShader')
        mix.inputs[0].default_value=transparent
        m.node_tree.links.new(tr.outputs[0],mix.inputs[1])
        m.node_tree.links.new(shader.outputs[0],mix.inputs[2])
        m.node_tree.links.new(mix.outputs[0],out.inputs[0])
    else:
        m.node_tree.links.new(shader.outputs[0],out.inputs[0])
    return m
 
black=material('Preto_mate',(0.008,0.008,0.01,1),0.95)
paper=material('Papel_marfim',(0.69,0.53,0.32,1))
cover=material('Capa_castanha',(0.12,0.045,0.018,1))
ink=material('Tinta',(0.035,0.02,0.01,1))
cyan=material('Sky_blue',(0.235,0.617,0.831,1),emission=3)
words=material('Texto_luminoso',(0.55,0.85,1,1),emission=2)
floor=material('Pavimento',(0.04,0.048,0.055,1),0.25)
screen=material('Tela_transparente',(0.235,0.617,0.831,1),emission=0.6,transparent=0.035)
 
def link(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    return obj
 
def box(name,loc,size,mat,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=link(bpy.context.object); o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.parent=parent; o.location=loc; o.data.materials.append(mat)
    bevel=o.modifiers.new('Arestas','BEVEL'); bevel.width=0.008; bevel.segments=3
    return o
 
def line(name,points,mat,radius=0.004,parent=None):
    data=bpy.data.curves.new(name,'CURVE'); data.dimensions='3D'
    data.bevel_depth=radius; data.bevel_resolution=3
    s=data.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,data); col.objects.link(o)
    o.parent=parent; data.materials.append(mat)
    return o
 
def text(name,body,loc,size,mat,parent=None,rot=(0,0,0)):
    data=bpy.data.curves.new(name,'FONT'); data.body=body
    data.size=size; data.align_x='CENTER'; data.align_y='CENTER'
    data.extrude=0.0003
    o=bpy.data.objects.new(name,data); col.objects.link(o)
    o.parent=parent; o.location=loc; o.rotation_euler=rot
    data.materials.append(mat)
    return o
 
def panel(name,loc,width,height,mat):
    x,y,z=loc
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x-width/2,y,z-height/2),(x+width/2,y,z-height/2),
                      (x+width/2,y,z+height/2),(x-width/2,y,z+height/2)],[],[(0,1,2,3)])
    mesh.update(); uv=mesh.uv_layers.new(name='UVMap')
    for face in mesh.polygons:
        for i,co in zip(face.loop_indices,[(0,0),(1,0),(1,1),(0,1)]): uv.data[i].uv=co
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); mesh.materials.append(mat)
    return o
 
# Não são criados painéis de galeria, bloco branco ou painel traseiro opaco.
box('Pavimento',(0,0,-0.06),(9,9,0.12),floor)
cx,cy=0.55,0.5
half=CUBO_LADO/2
cz=POSTE_ALTURA+half
# A secção inteira do poste coincide com a projeção horizontal do cubo.
box('Poste_PRETO_MATE',(cx,cy,POSTE_ALTURA/2),
    (CUBO_LADO,CUBO_LADO,POSTE_ALTURA),black)
for axis in range(3):
    other=[i for i in range(3) if i!=axis]
    for s1 in (-1,1):
        for s2 in (-1,1):
            a=[cx,cy,cz]; b=a.copy()
            a[axis]-=half; b[axis]+=half
            for idx,s in zip(other,(s1,s2)):
                a[idx]+=s*half; b[idx]+=s*half
            line('Aresta_cubo', [a,b],cyan)
# Casca constituída apenas por planos transparentes, nunca um bloco sólido.
panel('Tela_frontal_word_cloud',(cx,cy-half-0.002,cz),CUBO_LADO,CUBO_LADO,screen)
for x in (cx-half,cx+half):
    side=panel('Lateral_transparente',(0,0,0),CUBO_LADO,CUBO_LADO,screen)
    side.rotation_euler.z=math.pi/2; side.location=(x,cy,cz)
 
# Vídeo opcional num plano transparente; sem vídeo, não cria painel traseiro.
if VIDEO_PATH:
    path=Path(bpy.path.abspath(VIDEO_PATH))
    if not path.is_file(): raise FileNotFoundError(str(path))
    m=material('Video_transparente',(1,1,1,1),emission=0.9,transparent=0.55)
    tex=m.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(path),check_existing=True)
    tex.image.source='MOVIE'
    tex.image_user.use_auto_refresh=True; tex.image_user.use_cyclic=True
    tex.image_user.frame_start=1
    tex.image_user.frame_duration=max(1,tex.image.frame_duration)
    em=next(n for n in m.node_tree.nodes if n.type=='EMISSION')
    m.node_tree.links.new(tex.outputs['Color'],em.inputs[0])
    panel('Video_interior_transparente',(cx,cy+half-0.03,cz),CUBO_LADO*0.92,CUBO_LADO*0.92,m)
layout=[(0,.22,.071),(-.15,.12,.039),(.13,.10,.045),(0,-.01,.077),
        (-.18,-.12,.036),(.15,-.13,.037),(0,-.23,.046),(-.19,-.30,.027),
        (.21,.30,.033),(.16,-.31,.026)]
for i,(word,(dx,dz,size)) in enumerate(zip(PALAVRAS,layout)):
    text('WordCloud_'+str(i),word,(cx+dx,cy-half-.012,cz+dz),size,words,rot=(math.pi/2,0,0))
 
# Livro imediatamente à esquerda do cubo: folga entre extremidades de 8 cm.
book_width=1.24
bx=cx-half-FOLGA_LIVRO_CUBO-book_width/2
by=cy
box('Podio_livro_PRETO_MATE',(bx,by,.58),(.48,.48,1.16),black)
root=bpy.data.objects.new('Livro_inclinacao',None); col.objects.link(root)
root.location=(bx,by,1.20); root.rotation_euler.x=math.radians(20)
box('Apoio_livro_PRETO_MATE',(0,0,0),(book_width,.85,.045),black,root)
box('Capa_livro',(0,0,.035),(1.18,.79,.04),cover,root)
for sign in (-1,1): box('Paginas',(sign*.29,0,.09),(.565,.74,.075),paper,root)
line('Vinco',[(0,-.37,.135),(0,.37,.135)],cover,.006,root)
text('Titulo','UM LIVRO DE MEMÓRIAS',(-.28,.27,.133),.032,ink,root)
for i,word in enumerate(['Recordar','Descobrir','Sentir','Partilhar','Imaginar']):
    y=.18-i*.105
    text('Opcao_'+str(i),word,(-.28,y,.133),.029,ink,root)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.026,depth=.004)
    o=link(bpy.context.object); o.name='Sensor_pressao_'+str(i+1)
    o.parent=root; o.location=(.42,y,.132); o.data.materials.append(black)
    o['canal']=i+1; o['tipo']='Representação visual; sem ligação a hardware'
    pts=[(.42+.033*math.cos(a*math.tau/64),y+.033*math.sin(a*math.tau/64),.136) for a in range(65)]
    line('Indicador_sensor',pts,cyan if i==SENSOR_ATIVO else words,.002,root)
text('Pagina_direita','ESCUTA\n\nCada toque desperta\numa nova memória.',(.25,.24,.134),.031,ink,root)
# Fluxos compactos, adaptados à nova proximidade.
start=root.matrix_basis @ Vector((.59,.12,.14))
end=Vector((cx-half,cy,cz-.16))
for j in range(9):
    pts=[]
    for k in range(49):
        t=k/48; v=start.lerp(end,t)
        v.y+=.035*math.sin(t*8+j)*math.sin(math.pi*t)
        v.z+=.055*math.sin(t*7+j)*math.sin(math.pi*t)
        pts.append(tuple(v))
    line('Fluxo_luminoso',pts,cyan,.0015)
 
def light(name,loc,power,color,kind='AREA',target=(0,0,1)):
    data=bpy.data.lights.new(name,kind); data.energy=power; data.color=color
    if kind=='AREA': data.size=3
    else: data.shadow_soft_size=.15
    o=bpy.data.objects.new(name,data); col.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('Luz_livro',(-2,-2,4),450,(1,.78,.55))
light('Luz_geral',(2,-1,4),350,(.65,.8,1))
light('Interior_sky_blue',(cx,cy,cz),16,(.53,.81,.92),'POINT')
data=bpy.data.cameras.new('Camera_instalacao'); cam=bpy.data.objects.new('Camera_instalacao',data)
col.objects.link(cam); cam.location=(3.4,-6.5,3.0)
cam.rotation_euler=(Vector((-.35,.5,1.35))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=48; scene.camera=cam
scene.frame_set(1)
if OUTPUT_BLEND: bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUTPUT_BLEND))
print('Instalação atualizada: poste 0,90 x 0,90 m; livro junto ao cubo.')
