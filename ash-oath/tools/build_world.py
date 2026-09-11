"""Create Ash Oath's authored 3D assets in Blender, preserving editable .blend sources.
Run: Blender --background --python tools/build_world.py
Coordinates in helpers use game (x, z, height); exported glTF is Y-up.
"""
import bpy, math, random, json, pathlib
from mathutils import Vector
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'game/assets/models'
OUT.mkdir(parents=True, exist_ok=True)
random.seed(617)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
M = {}

def mat(name, color, metal=0.0, rough=.8, emission=0.0):
    # Authored palette is sRGB; Principled BSDF values are scene-linear.
    color=tuple(c**2.2 for c in color)
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if p is None:
        p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        output=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None) or m.node_tree.nodes.new('ShaderNodeOutputMaterial')
        m.node_tree.links.new(p.outputs['BSDF'],output.inputs['Surface'])
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    M[name]=m; return m

for name,c,metal,rough in [
 ('stone',(.27,.30,.28),0,.94),('stone_light',(.39,.40,.34),0,.95),('stone_dark',(.12,.15,.15),0,.96),
 ('wood',(.22,.12,.062),0,.83),('wood_cut',(.40,.27,.14),0,.83),('wood_dark',(.10,.075,.054),0,.9),
 ('iron',(.15,.19,.20),.75,.39),('steel',(.46,.52,.52),.82,.28),('gold',(.57,.35,.13),.72,.35),
 ('canvas',(.42,.37,.23),0,.98),('canvas_red',(.28,.075,.062),0,.97),('canvas_blue',(.11,.23,.28),0,.97),
 ('rope',(.49,.37,.23),0,1),('skin',(.57,.34,.22),0,.78),('pale',(.66,.50,.36),0,.83),
 ('leather',(.15,.073,.040),0,.89),('hair',(.08,.044,.024),0,.95),('fur',(.32,.27,.19),0,1),
 ('cloth',(.21,.20,.15),0,.95),('purple',(.27,.15,.29),0,.89),('red',(.38,.085,.046),0,.9),
 ('bone',(.60,.55,.38),0,.88),('green',(.12,.20,.15),0,.97),('pine',(.052,.13,.115),0,.97),
 ('pine_light',(.105,.19,.14),0,.96),('grass',(.21,.28,.16),0,1),('grass_dry',(.37,.34,.18),0,1),
 ('black',(.025,.034,.032),0,.96),('water',(.12,.22,.23),.3,.18)]: mat(name,c,metal,rough)
mat('ember',(1,.16,.013),0,.7,3);mat('fire',(1,.48,.035),0,.6,5)
mat('rune',(.26,.62,.69),0,.5,2)

# Bake subtle material grain into real images, so exported GLB matches Blender.
def grain(name,base,fabric=False):
    size=256;yy,xx=np.mgrid[:size,:size];rng=np.random.default_rng(len(name)*12)
    n=rng.normal(0,.02,(size,size))
    if fabric:n+=.025*np.sin(xx*math.pi/2)+.025*np.sin(yy*math.pi/2)+.05*np.sin(xx*.021+yy*.031)
    else:n+=.06*np.sin(xx*.17+np.sin(yy*.03))+.025*np.sin(xx*.5+yy*.007)
    c=np.clip(np.array(base)[None,None,:]*(1+n[:,:,None]*2),0,1)
    image=bpy.data.images.new(name+' grain',width=size,height=size)
    pixels=np.concatenate([c,np.ones((size,size,1))],axis=2).astype('float32')
    image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(ROOT/'game/assets/textures'/(name+'.png'));image.file_format='PNG';image.save();image.pack()
    nt=M[name].node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image
    nt.links.new(tex.outputs['Color'],next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'])
grain('wood',(.22,.12,.062));grain('wood_cut',(.40,.27,.14))
for name,base in [('canvas',(.42,.37,.23)),('canvas_red',(.28,.075,.062)),('canvas_blue',(.11,.23,.28)),('purple',(.27,.15,.29))]:grain(name,base,True)

def xyz(p): return (p[0],-p[1],p[2])
def material(o,m): o.data.materials.append(M[m] if isinstance(m,str) else m); return o
def smooth(o):
    for f in o.data.polygons:f.use_smooth=True
    return o
def cube(name,p,s,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.name=name;o.scale=(s[0],s[1],s[2])
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);material(o,m)
    if bevel:
        mod=o.modifiers.new('Worn edges','BEVEL');mod.width=bevel;mod.segments=2
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def cone(name,p,r1,r2,h,m,n=12):
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r1,radius2=r2,depth=h,location=xyz(p));o=bpy.context.object;o.name=name;material(o,m);return o
def uv(name,p,s,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1,location=xyz(p));o=bpy.context.object;o.name=name;o.scale=(s[0],s[1],s[2]);material(o,m);return smooth(o)
def rock(name,p,s,m='stone'):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=xyz(p));o=bpy.context.object;o.name=name;o.scale=(s[0],s[1],s[2]);o.rotation_euler=(random.random()*.3,random.random()*.3,random.random()*6.28);material(o,m);return o
def beam(name,a,b,r,m,n=8):
    v=Vector(xyz(b))-Vector(xyz(a));o=cone(name,((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2),r,r,v.length,m,n)
    o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o
def mesh(name,verts,faces,m):
    d=bpy.data.meshes.new(name);d.from_pydata([xyz(p) for p in verts],[],faces);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);material(o,m)
    d.uv_layers.new()
    for poly in d.polygons:
        for li in poly.loop_indices:
            v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x*.5,v.y*.4+v.z*.4)
    return o
def torus(name,p,r,t,m):
    bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=6,location=xyz(p),major_radius=r,minor_radius=t);o=bpy.context.object;o.name=name;material(o,m);return o
def empty(name,p,parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=xyz(p)
    if parent:o.parent=parent
    return o
def parent_keep(o,p):
    bpy.context.view_layer.update()
    w=o.matrix_world.copy();o.parent=p;o.matrix_world=w
    bpy.context.view_layer.update()
def export(name,objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_animations=False)
def join_static():
    # Merge by material: a rich environment without thousands of draw calls.
    for m in list(M.values()):
        obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and len(o.data.materials)==1 and o.data.materials[0]==m]
        if not obs:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in obs:o.select_set(True)
        bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name='Environment_'+m.name

obstacles=[]
def obstacle(x,z,w,d):obstacles.append([x,z,w,d])

# Multi-scale fractal noise generator (pure organic FFT synthesis, zero axis-aligned sine grids)
def fbm_fft(N, exponent=1.4, seed=42):
    rng = np.random.default_rng(seed)
    fx = np.fft.rfftfreq(N)
    fy = np.fft.fftfreq(N)
    FY, FX = np.meshgrid(fy, fx, indexing='ij')
    dist = np.sqrt(FX**2 + FY**2)
    dist[0, 0] = 1.0
    amp = 1.0 / (dist ** exponent)
    amp[0, 0] = 0.0
    phases = rng.uniform(0, 2*np.pi, amp.shape)
    field = np.fft.irfft2(amp * np.exp(1j * phases), s=(N, N))
    return (field - field.mean()) / (field.std() + 1e-6)

# Broad, textured ground; winding ochre tracks are baked into the exported material.
N = 2048
yy, xx = np.mgrid[0:N, 0:N]
X = xx / (N - 1) * 88 - 44
Z = yy / (N - 1) * 120 - 84

# Multi-scale fractal noise layers
warp_x = fbm_fft(N, 1.55, seed=71)
warp_z = fbm_fft(N, 1.55, seed=83)
macro = fbm_fft(N, 1.75, seed=97)
patch = fbm_fft(N, 1.35, seed=113)
micro = fbm_fft(N, 0.95, seed=127)

# Coordinate domain warping eliminates straight lines and geometric artifacts
X_w = X + warp_x * 1.6
Z_w = Z + warp_z * 1.6

# Winding organic dirt roads
road_cx = 1.2 * np.sin(Z * 0.18) + warp_x * 0.7
road_dist = np.abs(X - road_cx)
road_w = 2.1 + 0.45 * patch
p_road = np.clip(1.0 - (road_dist / road_w)**2.2, 0, 1)

# Secondary paths across camp
p_side1 = np.clip(1.0 - ((Z - 2 - 0.10 * X + warp_z * 0.4) / (2.4 + 0.4 * patch))**2, 0, 1) * np.exp(-(X / 16)**6)
p_side2 = np.clip(1.0 - ((Z + 7 - 0.13 * X + warp_z * 0.4) / (1.7 + 0.3 * patch))**2, 0, 1) * np.exp(-(X / 15)**6)
path = np.maximum(p_road, np.maximum(p_side1, p_side2))

# Central camp clearing & points of interest
camp_r = np.sqrt((X_w / 21)**2 + ((Z_w - 1) / 20)**2)
camp = np.clip(1.0 - camp_r**1.5, 0, 1)

# Fire pit ash/charcoal core
fire_r = np.sqrt((X + 1)**2 + (Z - 2)**2)
ash = np.exp(-(fire_r / 2.5)**2) * 0.85

# Charsi forge soot & coal cinders
forge_r = np.sqrt((X - 8.45)**2 + (Z - 8.0)**2)
soot = np.exp(-(forge_r / 3.2)**2) * 0.65

# Dirt factor
w_dirt = np.clip(path * 0.95 + camp * 0.32 + ash * 0.5 + soot * 0.4, 0, 1)

# Color palettes (Dark fantasy heath & moor)
c_grass_base = np.array([0.18, 0.24, 0.15])
c_grass_moss = np.array([0.13, 0.19, 0.12])
c_grass_dry = np.array([0.28, 0.27, 0.17])
c_dirt = np.array([0.33, 0.27, 0.19])
c_dirt_dark = np.array([0.22, 0.17, 0.12])
c_ash = np.array([0.08, 0.08, 0.07])

# Natural grass hue variations
t_grass = np.clip((macro * 0.5 + patch * 0.5 + 0.2) * 0.5, 0, 1)
grass_col = c_grass_base[None, None, :] * (1 - t_grass[:, :, None]) + c_grass_dry[None, None, :] * t_grass[:, :, None]
t_moss = np.clip(patch - 0.25, 0, 1)
grass_col = grass_col * (1 - t_moss[:, :, None] * 0.35) + c_grass_moss[None, None, :] * (t_moss[:, :, None] * 0.35)

# Natural dirt & soil variations
t_dirt = np.clip((patch * 0.6 + micro * 0.4 + 0.3) * 0.5, 0, 1)
dirt_col = c_dirt[None, None, :] * (1 - t_dirt[:, :, None]) + c_dirt_dark[None, None, :] * t_dirt[:, :, None]
t_ash = np.clip((ash + soot), 0, 1)[:, :, None]
dirt_col = dirt_col * (1 - t_ash) + c_ash[None, None, :] * t_ash

# Blend terrain surfaces with micro-soil grit
w_3d = w_dirt[:, :, None]
col = grass_col * (1 - w_3d) + dirt_col * w_3d + micro[:, :, None] * 0.02
col = np.clip(col, 0, 1)
rgba = np.concatenate([col, np.ones((N, N, 1))], axis=2).astype('float32')

im = bpy.data.images.new('Handpainted moor and paths', width=N, height=N)
im.pixels.foreach_set(rgba.ravel())
im.filepath_raw = str(ROOT / 'game/assets/textures/moor.png')
im.file_format = 'PNG'
im.save()

# Procedural surface normal map for micro-depth
height = (1.0 - w_dirt) * 0.03 + micro * 0.015 - p_road * 0.02
dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * (N / 88.0) * 0.5
dz = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * (N / 120.0) * 0.5
norm_x = -dx * 2.5
norm_z = -dz * 2.5
norm_y = np.ones_like(norm_x)
len_norm = np.sqrt(norm_x**2 + norm_y**2 + norm_z**2)
n_rgb = np.stack([(norm_x / len_norm * 0.5 + 0.5), (norm_z / len_norm * 0.5 + 0.5), (norm_y / len_norm * 0.5 + 0.5), np.ones((N, N))], axis=2).astype('float32')

im_norm = bpy.data.images.new('Handpainted moor normal', width=N, height=N)
im_norm.pixels.foreach_set(n_rgb.ravel())
im_norm.filepath_raw = str(ROOT / 'game/assets/textures/moor_normal.png')
im_norm.file_format = 'PNG'
im_norm.save()

ground = mat('ground', (1, 1, 1), rough=0.92)
nt = ground.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = im
nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
tex_norm = nt.nodes.new('ShaderNodeTexImage'); tex_norm.image = im_norm
tex_norm.image.colorspace_settings.name = 'Non-Color'
norm_node = nt.nodes.new('ShaderNodeNormalMap'); norm_node.inputs['Strength'].default_value = 0.75
nt.links.new(tex_norm.outputs['Color'], norm_node.inputs['Color'])
nt.links.new(norm_node.outputs['Normal'], bsdf.inputs['Normal'])

o = mesh('Moor ground', [(-44, -84, -.025), (44, -84, -.025), (44, 36, -.025), (-44, 36, -.025)], [(0, 3, 2, 1)], ground)
for poly in o.data.polygons:
    for li in poly.loop_indices:
        v = o.data.vertices[o.data.loops[li].vertex_index].co
        o.data.uv_layers.active.data[li].uv = ((v.x + 44) / 88, (-v.y + 84) / 120)

def barrel(x,z,sz=1):
    cone('Oak barrel',(x,z,.55*sz),.43*sz,.37*sz,1.1*sz,'wood',12)
    for h in [.15,.88]:torus('Barrel iron hoops',(x,z,h*sz),.414*sz,.032*sz,'iron')
    for i in range(12):
        a=i*math.tau/12;beam('Stave seam',(x+.422*sz*math.cos(a),z+.422*sz*math.sin(a),.16*sz),(x+.395*sz*math.cos(a),z+.395*sz*math.sin(a),.99*sz),.009,'wood_dark',4)
    cone('Barrel lid',(x,z,1.11*sz),.36*sz,.36*sz,.035,'wood_cut')
def crate(x,z,sz=.8):
    cube('Supplies crate',(x,z,sz/2),(sz,sz,sz),'wood_dark',.025)
    for dz in [-sz/2,sz/2]:
        for h in [.1,sz-.1]:cube('Crate edging',(x,z+dz,h),(sz+.03,.07,.10),'wood_cut',.015)
        beam('Crate cross brace',(x-sz*.38,z+dz,sz*.15),(x+sz*.38,z+dz,sz*.85),.055,'wood')
def tent(x,z,w,d,h,c='canvas'):
    # Pitched canopy with a scalloped hem, visible seams, open entrance and ropes.
    for side in [-1,1]:
        verts=[]
        for k in range(13):
            zz=z-d/2+d*k/12
            verts.extend([(x,zz,h-.12*math.sin(k/12*math.pi)),(x+side*w*.55,zz,.6-.09*(k%2))])
        o=mesh('Stitched canvas canopy',verts,[(i,i+1,i+3,i+2) for i in range(0,24,2)],c)
        sol=o.modifiers.new('Canvas thickness','SOLIDIFY');sol.thickness=.035
        for k in range(1,5):
            zz=z-d/2+d*k/5;beam('Canopy seam',(x,zz,h-.1),(x+side*w*.55,zz,.58),.015,'rope',5)
    for zz in [z-d/2,z+d/2]:
        beam('Tent ridge post',(x,zz,0),(x,zz,h+.24),.08,'wood_cut')
        for s in [-1,1]:
            beam('Guy rope',(x+s*w*.53,zz,.62),(x+s*(w*.65+.4),zz+.4,.08),.018,'rope',5)
            cone('Tent peg',(x+s*(w*.65+.4),zz+.4,.13),.05,.025,.3,'wood',6)
    mesh('Canvas back',[(x-w*.55,z-d/2,.05),(x+w*.55,z-d/2,.05),(x,z-d/2,h)],[(0,1,2)],c)
    cube('Woven ground rug',(x,z,.015),(w*.8,d*.82,.035),'red',.01)
    cube('Bedroll',(x-w*.23,z,.16),(.75,d*.68,.2),'cloth',.09)
    barrel(x+w*.70,z-d*.15,.8);crate(x+w*.69,z+d*.23,.7)
    obstacle(x,z,w*1.08,d)

tent(-9,-7,5.8,5.2,3.5,'purple')
tent(-12,6,4.8,5,2.8,'canvas_blue')
tent(11,-7,5.3,4.5,3.1,'canvas_red')
tent(13,8,5.5,5,3.3,'canvas')

# Apothecary: herb pots, ritual table, scrolls, candles.
cube('Akara table',(-8,-3.6,.85),(2.9,.85,.14),'wood',.06)
for x in [-9.15,-6.85]:beam('Table feet',(x,-3.6,0),(x,-3.6,.82),.075,'wood')
for i in range(7):
    x=-9.1+i*.34;cone('Potion flask',(x,-3.6,.99),.11,.065,.21,['green','purple','water'][i%3],10);cone('Flask cork',(x,-3.6,1.12),.045,.045,.06,'wood_cut')
for x in [-10,-6]:
    cone('Clay herb pot',(x,-3.0,.28),.28,.34,.55,'wood_cut')
    for k in range(7):beam('Dried herbs',(x,-3,.52),(x+random.uniform(-.3,.3),-3+random.uniform(-.3,.3),1.0+random.random()*.4),.022,'grass_dry',4)
obstacle(-8,-3.6,3.0,.9)

# Stone fire ring at the social heart of the camp.
for i in range(14):
    a=i*math.tau/14;rock('Fire ring',(-1+1.18*math.cos(a),2+1.18*math.sin(a),.18),(.32,.25,.2),'stone_light')
for i in range(5):
    a=i*math.pi/5;beam('Charred campfire logs',(-1-.7*math.cos(a),2-.7*math.sin(a),.2),(-1+.7*math.cos(a),2+.7*math.sin(a),.3),.13,'wood_dark')
for i in range(16):rock('Glowing coal',(-1+random.uniform(-.6,.6),2+random.uniform(-.6,.6),.18),(.12,.1,.08),'ember')
obstacle(-1,2,2.3,2.3)
for x,z in [(-4.3,2),(-1,5.4),(2.2,2.8)]:
    beam('Camp bench',(x-1,z,.42),(x+1,z,.42),.21,'wood')

# Charsi's forge, chimney and anvil.
for x in [7.2,9.7]:cube('Forge stone support',(x,8,.6),(.6,1.5,1.2),'stone',.06)
cube('Forge hearth',(8.45,8,1.2),(3.1,1.7,.4),'stone_dark',.10)
cube('Forge coal bed',(8.45,7.8,1.44),(2.2,1.0,.08),'ember')
cube('Forge chimney',(8.45,8.6,3),(1.6,.7,3.1),'stone',.07)
for j in range(7):cube('Chimney masonry',(8.45,8.2,1.7+j*.4),(1.7,.1,.06),'stone_dark')
cone('Anvil stump',(7,5.5,.35),.47,.42,.7,'wood',12)
cube('Anvil waist',(7,5.5,.88),(.6,.38,.4),'iron',.08)
cube('Anvil face',(7,5.5,1.13),(1.2,.58,.18),'steel',.06)
beam('Anvil horn',(7.4,5.5,1.1),(7.95,5.5,1.10),.12,'steel')
for x in [6,10]:barrel(x,9,.9)
obstacle(8.5,8.2,3.5,2.0);obstacle(7,5.5,1.3,.9)

# Merchant wagon: boards, iron-rimmed spoke wheels, curved cloth cover.
x,z=-8,11
cube('Wagon platform',(x,z,.83),(2.8,4.2,.22),'wood',.045)
for sx in [-1.35,1.35]:
    for h in [1.02,1.26,1.5]:cube('Wagon side boards',(x+sx,z,h),(.1,4.2,.19),'wood_cut',.02)
for zz in [-1.35,1.35]:
    beam('Wagon axle',(x-1.65,z+zz,.6),(x+1.65,z+zz,.6),.1,'iron')
    for sx in [-1.65,1.65]:
        o=torus('Iron wheel rim',(x+sx,z+zz,.61),.60,.047,'iron');o.rotation_euler[1]=math.pi/2
        o=torus('Oak wheel',(x+sx,z+zz,.61),.54,.10,'wood_cut');o.rotation_euler[1]=math.pi/2
        for k in range(8):
            a=k*math.tau/8;beam('Wagon wheel spoke',(x+sx,z+zz,.61),(x+sx,z+zz+math.cos(a)*.50,.61+math.sin(a)*.5),.032,'wood_cut')
verts=[]
for zz in [z-2,z+2]:
    for j in range(17):
        a=j/16*math.pi;verts.append((x+math.cos(a)*1.5,zz,1.45+math.sin(a)*1.45))
mesh('Wagon canvas',verts,[(j,j+1,j+18,j+17) for j in range(16)],'canvas')
for zz in [-2,-1,0,1,2]:
    for j in range(16):
        a=j/16*math.pi;b=(j+1)/16*math.pi;beam('Canvas rib',(x+math.cos(a)*1.515,z+zz,1.45+math.sin(a)*1.465),(x+math.cos(b)*1.515,z+zz,1.45+math.sin(b)*1.465),.022,'rope',5)
obstacle(x,z,3.5,4.5)
for i in range(6):crate(-11+i*.8,14+random.uniform(-.3,.3),.7)

# Palisade encloses the camp. A northern gate leads to Blood Moor.
for i in range(78):
    a=i/78*math.tau;x=20*math.cos(a);z=1+19*math.sin(a)
    if z<-15 and abs(x)<3.7:continue
    h=1.9+random.random()*.55
    cone('Sharpened oak palisade',(x,z,h/2),.20,.17,h-.25,'wood',7)
    cone('Palisade point',(x,z,h-.03),.18,0,.50,'wood_cut',7)
    if i%3==0:obstacle(x,z,.6,.6)
    b=(i+1)/78*math.tau;xx=20*math.cos(b);zz=1+19*math.sin(b)
    if not (zz<-15 and abs(xx)<3.7):
        for hrail in [.65,1.4]:beam('Continuous palisade rail',(x,z,hrail),(xx,zz,hrail),.09,'wood_dark')
        beam('Palisade diagonal brace',(x,z,.65),(xx,zz,1.4),.045,'wood')
for x in [-3.65,3.65]:
    cube('Gate pillar',(x,-17,1.9),(.60,.62,3.8),'wood_dark',.07)
    cone('Iron gate finial',(x,-17,4.03),.3,0,.5,'iron',6)
beam('Gate lintel',(-4,-17,3.5),(4,-17,3.5),.21,'wood')
for x in [-3.3,3.3]:
    beam('Banner post',(x,-16.8,3),(x,-16.8,4.8),.045,'iron')
    mesh('Rogue standard',[(x,-16.75,4.65),(x+1.1,-16.75,4.65),(x+1,-16.65,3.0),(x+.55,-16.8,3.4),(x,-16.7,3)],[(0,1,2,3,4)],'red')

# Waypoint and scattered human traces.
cone('Waypoint base',(6,-1,.05),1.8,1.8,.12,'stone_dark',12)
for i in range(8):
    a=i*math.tau/8;cube('Waypoint rune',(6+1.45*math.cos(a),-1+1.45*math.sin(a),.125),(.25,.08,.012),'rune')
torus('Waypoint ring',(6,-1,.13),1.3,.026,'rune')
for x,z in [(-16,-6),(-15,10),(14,-2),(10,12),(-6,-10),(5,-12)]:
    barrel(x,z,.8+random.random()*.2);crate(x+.8,z+.5,.65)

def pine(x,z,h):
    cone('Pine trunk',(x,z,h*.38),.22,.12,h*.76,'wood_dark',7)
    for j in range(4):
        o=cone('Pine boughs',(x,z,h*(.38+j*.14)),h*(.29-j*.043),0,h*.41,['pine','pine_light'][j%2],13);o.rotation_euler[2]=j*.83
        for v in o.data.vertices:
            if v.co.z<0:
                v.co.x*=random.uniform(.78,1.14);v.co.y*=random.uniform(.78,1.14);v.co.z+=random.uniform(-.14,.14)
for i in range(165):
    x=random.uniform(-41,41);z=random.uniform(-81,30)
    if (x/22)**2+((z-1)/21)**2<1.05:continue
    if z<-17 and abs(x)<24:continue
    pine(x,z,random.uniform(4,8));obstacle(x,z,.9,.9)
for i in range(85):
    x=random.uniform(-41,41);z=random.uniform(-80,29)
    if abs(x)<4:continue
    if (x/22)**2+((z-1)/21)**2<.9:continue
    rock('Weathered border boulder',(x,z,.35),(.55+random.random(),.5+random.random(),.5+random.random()*.9))
# Batch grass blades and cluster them naturally near borders, trees, rocks and clear of main paths
grass_verts = {'grass': [], 'grass_dry': []}
grass_faces = {'grass': [], 'grass_dry': []}

for i in range(1300):
    x = random.uniform(-37, 37)
    z = random.uniform(-76, 27)
    if abs(x - 1.2 * math.sin(z * .18)) < 2.3 or abs(z - 2 - .1 * x) < 2.3:
        continue
    mat_key = 'grass' if i % 3 else 'grass_dry'
    v_list = grass_verts[mat_key]
    f_list = grass_faces[mat_key]
    num_blades = random.randint(2, 4)
    for k in range(num_blades):
        a = random.random() * math.tau
        h = random.uniform(0.12, 0.40)
        dx = math.cos(a) * 0.045
        dz = math.sin(a) * 0.045
        base_idx = len(v_list)
        v_list.extend([
            (x - dx, z - dz, 0.0),
            (x + dx, z + dz, 0.0),
            (x + dx * 1.8, z + dz * 1.8, h)
        ])
        f_list.append((base_idx, base_idx + 1, base_idx + 2))

if grass_verts['grass']:
    mesh('Grass clump green', grass_verts['grass'], grass_faces['grass'], 'grass')
if grass_verts['grass_dry']:
    mesh('Grass clump dry', grass_verts['grass_dry'], grass_faces['grass_dry'], 'grass_dry')
for i in range(180):
    x=random.uniform(-17,17);z=random.uniform(-15,17)
    if random.random()<.5 and abs(x)>4:continue
    rock('Path pebbles',(x,z,.018),(.10+random.random()*.1,.08,.04),'stone_light' if i%3 else 'stone_dark')

# Ruined arch at the edge of the moor: the next story destination.
for x in [-2.1,2.1]:
    for k in range(5):cube('Den entrance masonry',(x,-72,k*.7+.35),(.85,1.0,.66),'stone_dark',.10)
for i in range(9):
    a=i*math.pi/8;o=cube('Den entrance keystone',(math.cos(a)*2.1,-72,3.0+math.sin(a)*1.5),(.80,1,.70),'stone',.08);o.rotation_euler[1]=a
cube('Den darkness',(0,-72.5,1.8),(3.6,.15,3.6),'black')
for i in range(16):
    x=random.uniform(-5.5,5.5);z=random.uniform(-75,-72.7);rock('Den crag',(x,z,1.3),(1.5,1.8,1.6),'stone_dark')

# Landmarks in the enlarged moor: collapsed farm, burial circle and a ruined road.
for x,z in [(-14,-38),(18,-54)]:
    for side in [-1,1]:
        for j in range(6):
            if j==3 and side==1:continue
            cube('Ruined farm masonry',(x+side*3,z+j*.75-2,random.uniform(.4,.8)),(.7,.73,random.uniform(.7,1.4)),'stone',.07)
        obstacle(x+side*3,z,.85,5.5)
    for j in range(4):beam('Collapsed roof rafters',(x-2+j*1.2,z-2,.18),(x-1+j*.8,z+2,.42),.085,'wood_dark')
    barrel(x+1,z, .85);crate(x-1.5,z-1,.7)
for i in range(12):
    a=i*math.tau/12;x=-17+math.cos(a)*3.6;z=-60+math.sin(a)*3.6
    o=cube('Forgotten grave',(x,z,.38),(.55,.25,.75),'stone_light',.04);o.rotation_euler[2]=-a
def flagstone(name, x, z, r, h, m='stone'):
    n = random.randint(5, 7)
    bot_verts = []
    top_verts = []
    for i in range(n):
        ang = i * math.tau / n + random.uniform(-0.25, 0.25)
        dist = r * random.uniform(0.75, 1.25)
        px = x + dist * math.cos(ang)
        pz = z + dist * math.sin(ang)
        bot_verts.append((px, pz, -0.025))
        top_verts.append((px, pz, h + random.uniform(-0.003, 0.003)))
    verts = bot_verts + top_verts
    faces = []
    for i in range(n):
        nxt = (i + 1) % n
        faces.append((i, nxt, n + nxt, n + i))
    faces.append(tuple(range(n, 2 * n)))
    faces.append(tuple(reversed(range(n))))
    return mesh(name, verts, faces, m)

# Ancient ruined road: broken, wind-worn flagstone clusters half-sunken in the moor earth
stone_mats = ['stone', 'stone_dark', 'stone_light']
for cluster_idx in range(16):
    cluster_z = -67.0 + cluster_idx * 2.9 + random.uniform(-0.6, 0.6)
    road_center_x = 1.2 * math.sin(cluster_z * 0.18)
    num_stones = random.randint(3, 6)
    for s_idx in range(num_stones):
        sx = road_center_x + random.uniform(-1.25, 1.25)
        sz = cluster_z + random.uniform(-0.8, 0.8)
        radius = random.uniform(0.28, 0.55)
        stone_h = random.uniform(0.008, 0.022)
        sm = random.choice(stone_mats)
        flagstone('Ancient flagstone', sx, sz, radius, stone_h, sm)
    for ch in range(random.randint(2, 4)):
        cx = road_center_x + random.uniform(-1.6, 1.6)
        cz = cluster_z + random.uniform(-1.0, 1.0)
        rock('Stone chip', (cx, cz, 0.01), (random.uniform(0.08, 0.16), random.uniform(0.06, 0.12), 0.03), random.choice(stone_mats))
obstacle(0,-74,11,4)
join_static()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/rogue_encampment.blend'))
export('rogue_encampment',list(bpy.context.scene.objects))
(ROOT/'game/data/world.json').write_text(json.dumps({'obstacles':obstacles,'bounds':[-38,-78,38,28]},indent=2))

# Characters: editable articulated mesh parts, detailed silhouettes, runtime pose animation.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def character(name,kind):
    before=set(bpy.context.scene.objects);root=empty('Figure',(0,0,0))
    hero=kind=='barbarian';enemy=kind=='fallen';robe=kind in ['akara','warriv']
    skin='red' if enemy else 'skin' if hero else 'pale'
    cloth='purple' if kind=='akara' else 'canvas_blue' if kind=='warriv' else 'red' if kind=='kashya' else 'leather'
    width=.48 if hero else .35
    torso=empty('Torso',(0,0,1.13),root)
    def part(o,p):parent_keep(o,p);return o
    part(uv('Chest',(0,0,1.43),(width,.27,.44),skin if hero or enemy else cloth),torso)
    if hero:
        for s in [-1,1]:
            part(uv('Pectoral',(s*.225,-.20,1.56),(.255,.13,.20),skin),torso)
            for j in range(3):part(uv('Abdominal muscles',(s*.115,-.245,1.30-j*.11),(.105,.055,.075),skin),torso)
        part(beam('Leather baldric',(-.35,-.25,1.78),(.29,-.29,1.09),.075,'leather'),torso)
    part(cone('Waist belt',(0,0,1.01),.33,.34,.14,'leather',12),torso)
    part(cube('Belt clasp',(0,-.32,1.02),(.17,.07,.16),'gold',.025),torso)
    part(cone('Layered skirt',(0,0,.89),.43,.31,.28,cloth,12),torso)
    if robe:part(cone('Long layered robe',(0,0,.66),.47,.28,1.15,cloth,16),torso)
    part(uv('Neck',(0,0,1.83),(.14,.13,.17),skin),torso)
    part(uv('Head',(0,-.015,2.05),(.22,.20,.29),skin),torso)
    part(uv('Nose',(0,-.205,2.05),(.065,.088,.09),skin),torso)
    for s in [-1,1]:
        part(uv('Ear',(s*.225,0,2.07),(.06,.055,.10),skin),torso)
        part(cube('Brow',(s*.095,-.189,2.14),(.13,.038,.045),'hair',.012),torso)
        part(uv('Eye',(s*.094,-.199,2.105),(.028,.018,.022),'ember' if enemy else 'black'),torso)
    if not enemy:
        part(uv('Hair cap',(0,.036,2.20),(.23,.22,.17),'hair'),torso)
        if hero:
            part(uv('Beard',(0,-.14,1.87),(.16,.13,.20),'hair'),torso)
            for s in [-1,1]:
                for j in range(5):part(uv('Braided hair',(s*.22,.09,2.10-j*.13),(.055,.06,.08),'hair'),torso)
            part(cube('War paint',(0,-.211,2.18),(.042,.025,.20),'red',.01),torso)
    else:
        for s in [-1,1]:part(beam('Demon horns',(s*.17,.02,2.25),(s*.40,.06,2.54),.07,'bone'),torso)
    if kind=='akara':
        part(uv('Hood',(0,.075,2.13),(.29,.24,.33),'purple'),torso)
        # Face remains exposed on the forward side of the hood.
        part(torus('Bronze pendant',(0,-.29,1.5),.085,.019,'gold'),torso)
    for s,tag in [(-1,'L'),(1,'R')]:
        hip=empty('Hip_'+tag,(s*.18,0,.96),root)
        part(uv('Thigh',(s*.20,0,.72),(.18,.18,.32),skin if hero or enemy else cloth),hip)
        part(uv('Boot',(s*.20,-.025,.29),(.175,.19,.30),'leather'),hip)
        part(cube('Foot',(s*.20,-.12,.11),(.32,.50,.19),'leather',.07),hip)
        part(cube('Shin guard',(s*.20,-.178,.36),(.21,.09,.31),'iron',.04),hip)
        shoulder=empty('Shoulder_'+tag,(s*(width+.035),0,1.70),torso)
        shoulder.matrix_world.translation=xyz((s*(width+.035),0,1.70))
        part(uv('Upper arm',(s*(width+.11),0,1.48),(.18 if hero else .125,.15,.29),skin),shoulder)
        part(uv('Forearm',(s*(width+.15),-.03,1.11),(.14,.14,.26),skin),shoulder)
        part(cone('Bracer',(s*(width+.15),-.03,1.10),.155,.17,.23,'iron',10),shoulder)
        part(uv('Hand',(s*(width+.16),-.045,.88),(.12,.11,.15),skin),shoulder)
        if hero or kind in ['kashya','charsi']:
            part(uv('Shoulder armor',(s*(width+.025),.005,1.73),(.25,.27,.16),'iron'),shoulder)
            for k in range(4):part(uv('Armor rivet',(s*(width+.025)+math.cos(k*1.5)*.17,-.20,1.74),(.025,.025,.025),'gold'),shoulder)
        if s==1:
            if kind=='akara':
                part(beam('Oak staff',(.54,-.06,.04),(.54,-.06,2.5),.043,'wood_cut'),shoulder)
                part(uv('Staff stone',(.54,-.06,2.51),(.09,.08,.13),'rune'),shoulder)
            elif kind=='warriv':part(uv('Travel satchel',(.46,0,.87),(.20,.16,.22),'wood_cut'),shoulder)
            else:
                part(beam('Weapon haft',(width+.16,-.045,.5),(width+.16,-.045,1.63),.044,'wood_cut'),shoulder)
                wx=width+.16
                if kind=='charsi':part(cube('Smith hammer',(wx,-.045,1.57),(.46,.23,.24),'steel',.035),shoulder)
                elif kind=='kashya':
                    part(beam('Rogue spear',(wx,-.045,.4),(wx,-.045,2.55),.035,'wood'),shoulder)
                    part(cone('Spearhead',(wx,-.045,2.66),.09,0,.37,'steel',4),shoulder)
                else:
                    part(mesh('Forged axe blade',[(wx,-.06,1.48),(wx+.34,-.06,1.74),(wx+.48,-.06,1.59),(wx+.43,-.06,1.23),(wx,-.06,1.34),(wx,-.16,1.48),(wx+.34,-.16,1.74),(wx+.48,-.16,1.59),(wx+.43,-.16,1.23),(wx,-.16,1.34)],[(0,1,2,3,4),(9,8,7,6,5),(1,6,7,2),(2,7,8,3),(3,8,9,4),(0,5,6,1)],'steel'),shoulder)
        elif hero:
            part(beam('Offhand blade',(s*(width+.16),-.045,.60),(s*(width+.16),-.045,1.33),.04,'steel',4),shoulder)
    if hero:
        part(beam('Back greatsword',(-.30,.30,.70),(.36,.30,2.14),.055,'steel',4),torso)
        part(beam('Back sword guard',(.06,.30,1.62),(.54,.30,1.43),.045,'gold'),torso)
        for k in range(8):part(uv('Fur mantle',(-.36+k*.10,.20,1.78+math.sin(k)*.02),(.105,.14,.09),'fur'),torso)
    obs=list(set(bpy.context.scene.objects)-before)
    # Merge static pieces sharing an articulation pivot and material.
    batches={}
    for o in obs:
        if o.type=='MESH':batches.setdefault((o.parent,o.data.materials[0]),[]).append(o)
    for (parent,m),parts in batches.items():
        if len(parts)<2:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in parts:o.select_set(True)
        bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
    obs=list(set(bpy.context.scene.objects)-before)
    export(name,obs)
    return obs

for name,kind in [('akara','akara'),('kashya','kashya'),('charsi','charsi'),('warriv','warriv'),('fallen','fallen')]:
    character(name,kind)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art'/f'{name}.blend'))
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
print('ASH OATH: Blender environment and six articulated figures exported.')
