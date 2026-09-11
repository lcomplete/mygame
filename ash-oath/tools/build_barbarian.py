"""Author the Ashen Oath barbarian in Blender from CC0 anatomical topology.
Preserves UVs, 163-bone skin weights, fitted equipment and ten animation clips.
Run Blender --background --python-exit-code 1 --python tools/build_barbarian.py.
"""
import bpy, json, math, random
import numpy as np
from pathlib import Path
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]; REF=ROOT/'art/reference/makehuman'; OUT=ROOT/'game/assets/models'
random.seed(912)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Read the body only. The original OBJ also contains joint locators and proxy cages.
verts=[]; texcoords=[]; faces=[]; face_uv=[]; group=''
for line in (REF/'base.obj').read_text().splitlines():
 t=line.split()
 if not t:continue
 if t[0]=='v':verts.append(list(map(float,t[1:4])))
 elif t[0]=='vt':texcoords.append(list(map(float,t[1:3])))
 elif t[0]=='g':group=t[1]
 elif t[0]=='f' and group=='body':
  faces.append([int(v.split('/')[0])-1 for v in t[1:]])
  face_uv.append([int(v.split('/')[1])-1 for v in t[1:]])
v=np.array(verts,dtype=float)
for name,weight in [('male-young.target',1.0),('muscle.target',.94),('mass.target',.64)]:
 for line in (REF/name).read_text().splitlines():
  t=line.split()
  if len(t)==4 and t[0].isdigit():v[int(t[0])]+=np.array(list(map(float,t[1:]))) * weight
scale=2.16/(v[:,1].max()-v[:,1].min())
# Towering, broad northern berserker proportions, preserving joint locations.
v[:,0]*=1.18
v[:,2]*=1.10
v=np.column_stack((v[:,0]*scale,-v[:,2]*scale,(v[:,1]-v[:,1].min())*scale))
used=sorted(set(i for f in faces for i in f));remap={old:new for new,old in enumerate(used)}
# Sculpt continuous anatomy: colossal traps, deltoids, chiseled pectorals, 6-pack abs, lats, and deep-set warrior brow & jaw
for i in used:
 x,y,z=v[i];ax=abs(x);front=max(0.0,min(1.0,-y/.08));back=max(0.0,min(1.0,y/.08))
 # Trapezius & neck
 traps=math.exp(-((z-1.76)/.14)**2)*math.exp(-((ax-.18)/.14)**2)
 v[i,2]+=0.024*traps;v[i,0]*=1.0+0.05*traps
 if 1.78<=z<=1.94 and ax<.16:
  v[i,0]*=1.0+0.07*math.exp(-((z-1.86)/.08)**2)
  v[i,1]-=0.015*front*math.exp(-((z-1.86)/.08)**2)
 # Deltoids
 delt=math.exp(-((z-1.70)/.13)**2)*math.exp(-((ax-.40)/.12)**2)
 v[i,0]*=1.0+0.10*delt;v[i,1]+=0.020*(back-front)*delt
 # Pectorals with sternum cleft
 chest=math.exp(-((z-1.62)/.16)**4)*math.exp(-(ax/.38)**4)
 v[i,0]*=1.0+0.08*chest*math.exp(-(ax/.44)**6)
 pec_cleft=1.0-math.exp(-((ax)/.045)**2)
 v[i,1]-=0.046*front*chest*pec_cleft
 # 6-Pack Abdominals & Linea Alba
 if 1.22<=z<=1.54 and ax<.16:
  linea_alba=1.0-math.exp(-((ax)/.028)**2)
  ab_furrow=sum(0.018*math.exp(-((z-lvl)/.024)**2) for lvl in [1.32,1.40,1.48])
  ab_bulge=math.exp(-((ax-.065)/.042)**2)*(0.022-ab_furrow)
  v[i,1]-=front*linea_alba*max(-0.015,ab_bulge)
 # Latissimus dorsi (V-taper)
 lats=math.exp(-((z-1.50)/.18)**2)*math.exp(-((ax-.28)/.12)**2)
 v[i,0]*=1.0+0.07*lats;v[i,1]+=0.032*back*lats
 # Facial structure: prominent brow ridge, deep eye sockets, rugged jaw
 if 2.00<=z<=2.08 and ax<.10:v[i,1]-=0.018*math.exp(-((z-2.035)/.028)**2)*math.exp(-((ax-.045)/.045)**2)*front
 if 1.96<=z<=2.02 and .025<=ax<=.085:v[i,1]+=0.012*math.exp(-((z-1.995)/.022)**2)*math.exp(-((ax-.052)/.024)**2)*front
 if 1.80<=z<=1.92:
  jaw=math.exp(-((z-1.86)/.06)**2);v[i,0]*=1.0+0.08*jaw
  if ax<.08:v[i,1]-=0.012*jaw*front
bodyverts=[v[i].tolist() for i in used];bodyfaces=[[remap[i] for i in f] for f in faces]
M={}
def mat(name,c,metal=0,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True
 nt=m.node_tree;p=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not p:
  p=nt.nodes.new('ShaderNodeBsdfPrincipled');o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(p.outputs['BSDF'],o.inputs['Surface'])
 p.inputs['Base Color'].default_value=(*[x**2.2 for x in c],1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 m.diffuse_color=(*[x**2.2 for x in c],1);M[name]=m;return m
skin=mat('Weathered skin · 2K albedo',(.68,.48,.36),0,.72)
leather=mat('Oiled oxhide',(.26,.17,.10),0,.82)
edge=mat('Leather cut edges',(.34,.22,.12),0,.80)
steel=mat('Hammered blue steel',(.29,.31,.30),.78,.48)
silver=mat('Honed edge',(.75,.78,.77),.92,.20)
bronze=mat('Old brass',(.43,.34,.22),.72,.49)
cloth=mat('Charcoal wool',(.11,.12,.13),0,.94)
hair=mat('Dark warrior hair',(.07,.045,.03),0,.78)
hairlight=mat('Grizzled hair highlights',(.20,.15,.11),0,.76)
fur=mat('Wolf underfur',(.20,.20,.18),0,1)
fur_light=mat('Wolf guard hairs',(.48,.46,.40),0,.95)
paint=mat('Nordic woad war paint',(.06,.14,.20),0,.84)
scar=mat('Healed scar tissue',(.52,.33,.26),0,.68)
tread=mat('Heavy boot tread',(.09,.08,.07),0,.88)
eye_mat=mat('Ivory sclera',(.78,.74,.68),0,.22)
iris_mat=mat('Fierce steel iris',(.16,.32,.36),0,.20)
black=mat('Pupil',(.01,.01,.01),0,.12)
# A tiled micro-normal map survives glTF export, unlike procedural shader nodes.
N=512; yy,xx=np.mgrid[:N,:N];rng=np.random.default_rng(2)
height=rng.normal(0,.14,(N,N))+.14*np.sin(xx*.51)*np.cos(yy*.39)+.06*np.sin(xx*1.8)*np.sin(yy*1.8)
dy,dx=np.gradient(height);normal=np.dstack((-dx,-dy,np.ones_like(dx)));normal/=np.linalg.norm(normal,axis=2)[:,:,None]
a=np.dstack((normal*.5+.5,np.ones((N,N)))).astype('float32')
im=bpy.data.images.new('Leather grain normal',width=N,height=N);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(a.ravel());im.filepath_raw=str(ROOT/'game/assets/textures/hero_grain_normal.png');im.file_format='PNG';im.save();im.pack()
for m in [leather,cloth,steel,bronze,skin,tread]:
 nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');t=nt.nodes.new('ShaderNodeTexImage');t.image=im
 n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.09 if m==skin else .28;nt.links.new(t.outputs['Color'],n.inputs['Color']);nt.links.new(n.outputs['Normal'],p.inputs['Normal'])
 if m==skin and 'Subsurface Weight' in p.inputs:
  p.inputs['Subsurface Weight'].default_value=.18;p.inputs['Subsurface Radius'].default_value=(1.0,.45,.25);p.inputs['Subsurface Scale'].default_value=.05
skinpath=REF/'system/skins/middleage_caucasian_male/middleage_lightskinned_male_diffuse.png'
if not skinpath.exists():
 candidates=list((REF/'system').rglob('*caucasian_male*diffuse.png')) if (REF/'system').exists() else []
 if candidates:skinpath=candidates[0]
if skinpath.exists():
 im=bpy.data.images.load(str(skinpath));im.scale(2048,2048);im.pack();nt=skin.node_tree;t=nt.nodes.new('ShaderNodeTexImage');t.image=im;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.74,.67,.61,1);nt.links.new(t.outputs['Color'],mix.inputs[1]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
else:print('NOTICE: anatomical skin image missing; using skin base color')
def mesh(name,vs,fs,m):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(m)
 for p in d.polygons:p.use_smooth=True
 return o
body=mesh('Anatomy · continuous weighted surface',bodyverts,bodyfaces,skin)
uv=body.data.uv_layers.new(name='UVMap')
for poly,ids in zip(body.data.polygons,face_uv):
 for li,t in zip(poly.loop_indices,ids):uv.data[li].uv=texcoords[t]
bvh=BVHTree.FromPolygons([Vector(p) for p in bodyverts],bodyfaces)
# Use the authored MakeHuman rig and weights rather than automatic proximity skinning.
skel=json.loads((REF/'default.mhskel').read_text());weights=json.loads((REF/'default_weights.mhw').read_text())['weights']
data=bpy.data.armatures.new('Barbarian skeleton');rig=bpy.data.objects.new('Barbarian_Rig',data);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def joint(name):return Vector(np.mean(v[skel['joints'][name]],axis=0))
for name,info in skel['bones'].items():
 b=data.edit_bones.new(name);b.head=joint(info['head']);b.tail=joint(info['tail'])
 if (b.tail-b.head).length<.0001:b.tail.z+=.01
 # Deterministic bone roll makes exported animation independent of UI locale.
 b.align_roll(Vector((0,-1,0)))
for name,info in skel['bones'].items():
 if info['parent']:data.edit_bones[name].parent=data.edit_bones[info['parent']]
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
def skin_bind(o,ids=None,bone=None):
 if bone:
  g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
 elif ids is not None:
  mapping={old:new for new,old in enumerate(ids)}
  for name,entries in weights.items():
   g=o.vertex_groups.new(name=name)
   for idx,w in entries:
    if idx in mapping:g.add([mapping[idx]],w,'REPLACE')
 mod=o.modifiers.new('Deform with anatomical skeleton','ARMATURE');mod.object=rig;o.parent=rig
 return o
skin_bind(body,used)
# One subdivision level gives face, hands and shoulders smooth, continuous silhouettes.
sub=body.modifiers.new('Anatomical refinement','SUBSURF');sub.levels=1;sub.render_levels=1
bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_move_up(modifier=sub.name)
# Equipment must be projected onto the exact exported smooth surface. Projecting
# onto the low-resolution cage leaves straps and paint buried in the skin.
bpy.ops.object.modifier_apply(modifier=sub.name)
body.data.calc_loop_triangles()
bvh=BVHTree.FromPolygons([p.co for p in body.data.vertices],[t.vertices for t in body.data.loop_triangles],all_triangles=True)
def fit_uv(o):
 if not o.data.uv_layers:
  uv=o.data.uv_layers.new()
  for p in o.data.polygons:
   for i in p.loop_indices:
    c=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(c.x*3+c.y,c.z*3)
def rigid(o,bone='spine03'):
 fit_uv(o);return skin_bind(o,bone=bone)
def sphere(name,p,s,m,bone='head',seg=20,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return rigid(o,bone)
def cube(name,p,s,m,bone='spine03',bevel=.005):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Forged rounded edge','BEVEL');mod.width=bevel;mod.segments=4;bpy.ops.object.modifier_apply(modifier=mod.name)
  for f in o.data.polygons:f.use_smooth=True
  mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return rigid(o,bone)
def tube(name,points,radii,m,bone='head',sides=7):
 vs=[];fs=[]
 for i,p in enumerate(points):
  p=Vector(p);d=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
  if d.length<.0001:d=Vector((0,0,1))
  q=d.to_track_quat('Z','Y')
  for k in range(sides):vs.append(tuple(p+q@Vector((math.cos(k*math.tau/sides)*radii[i],math.sin(k*math.tau/sides)*radii[i],0))))
 for i in range(len(points)-1):
  for k in range(sides):a=i*sides+k;b=i*sides+(k+1)%sides;fs.append((a,b,b+sides,a+sides))
 fs.append(tuple(range(sides-1,-1,-1)));fs.append(tuple((len(points)-1)*sides+k for k in range(sides)))
 return rigid(mesh(name,vs,fs,m),bone)
def ring(name,p,rx,ry,t,m,bone='spine05'):
 pts=[Vector((p[0]+rx*math.cos(i*math.tau/48),p[1]+ry*math.sin(i*math.tau/48),p[2])) for i in range(49)]
 return tube(name,pts,[t]*49,m,bone,6)
# Equipment is authored against the same body and skeleton in rest space.
exec(compile((Path(__file__).parent/'barbarian_equipment.py').read_text(), 'barbarian_equipment.py', 'exec'))
# Apply non-armature modifiers, then merge all accessory meshes by material.
# A real hero keeps ~15 surfaces instead of thousands of little draw calls.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):
  if mod.type!='ARMATURE':bpy.ops.object.modifier_apply(modifier=mod.name)
for m in M.values():
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0]==m]
 if len(obs)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=m.name
exec(compile((Path(__file__).parent/'barbarian_animation.py').read_text(), 'barbarian_animation.py', 'exec'))
# Export evaluated, skinned geometry and individual named actions.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in ['MESH','ARMATURE']:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'barbarian.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=True,export_animation_mode='ACTIONS',export_nla_strips=True,export_force_sampling=True,export_frame_range=False,export_skins=True,export_apply=False)
# Blender's glTF exporter flattens the linked color texture but drops a MixRGB
# multiply factor. Preserve the authored skin tint as the standard glTF factor.
import struct
path=OUT/'barbarian.glb';blob=path.read_bytes();length=struct.unpack_from('<I',blob,12)[0]
doc=json.loads(blob[20:20+length]);tail=blob[20+length:]
for m in doc['materials']:
 if m['name'].startswith('Weathered skin'):m['pbrMetallicRoughness']['baseColorFactor']=[.74,.67,.61,1]
chunk=json.dumps(doc,separators=(',',':'),ensure_ascii=True).encode();chunk+=b' '*((-len(chunk))%4)
path.write_bytes(struct.pack('<4sII',b'glTF',2,20+len(chunk)+len(tail))+struct.pack('<I4s',len(chunk),b'JSON')+chunk+tail)
# Keep an artist-friendly source scene and a reproducible close-up render.
rig.animation_data.action=bpy.data.actions['Idle'];bpy.context.scene.frame_set(1)
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='Studio ground';floor.data.materials.append(mat('Studio slate',(.10,.115,.12),0,.82))
world=bpy.context.scene.world or bpy.data.worlds.new('Studio');bpy.context.scene.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.08,.09,.11,1);bg.inputs[1].default_value=.35
for name,pos,power,color,size in [('Key',(3,-4,5),430,(1,.82,.65),4),('Fill',(-3,-2,3),230,(.56,.72,1),3),('Rim',(1,3,4),600,(.8,.88,1),2)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Portrait camera');cam=bpy.data.objects.new('Portrait camera',d);bpy.context.collection.objects.link(cam);cam.location=(2.6,-5.8,2.7);cam.rotation_euler=(Vector((0,0,1.16))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=2.85;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1100;scene.render.resolution_y=1300;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.filepath=str(ROOT/'artifacts/barbarian-portrait.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/barbarian.blend'))
print('HERO meshes',len([o for o in scene.objects if o.type=='MESH']),'triangles',sum(len(o.data.polygons)*2 for o in scene.objects if o.type=='MESH'),'bones',len(rig.data.bones),flush=True)
bpy.ops.render.render(write_still=True)
print('ASHEN OATH: anatomical barbarian exported and portrait rendered.')
