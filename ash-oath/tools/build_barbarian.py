"""Author the Ashen Oath barbarian in Blender from CC0 anatomical topology.
Preserves UVs, 163-bone skin weights, fitted equipment and seven animation clips.
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
for name,weight in [('male-young.target',1.0),('muscle.target',.65),('mass.target',.6)]:
 for line in (REF/name).read_text().splitlines():
  t=line.split()
  if len(t)==4 and t[0].isdigit():v[int(t[0])]+=np.array(list(map(float,t[1:]))) * weight
scale=2.15/(v[:,1].max()-v[:,1].min())
# Broad northern warrior proportions, preserving all joint locations.
v[:,0]*=1.17
v[:,2]*=1.08
v=np.column_stack((v[:,0]*scale,-v[:,2]*scale,(v[:,1]-v[:,1].min())*scale))
used=sorted(set(i for f in faces for i in f));remap={old:new for new,old in enumerate(used)}
# Sculpt the continuous surface: deltoids, pectorals, abdominal furrows and a broad jaw.
# Offsets are smooth fields; no separate sphere muscles are added.
for i in used:
 x,y,z=v[i];ax=abs(x)
 chest=math.exp(-((z-1.64)/.19)**4)
 v[i,0]*=1+.09*chest*math.exp(-(ax/.45)**6)
 front=max(0,min(1,-y/.09))
 v[i,1]-=.035*front*math.exp(-((ax-.19)/.12)**2-((z-1.60)/.08)**2)
 a=0
 for level in [1.32,1.40,1.48]:a+=.020*math.exp(-((ax-.065)/.042)**2-((z-level)/.026)**2)
 v[i,1]-=a*front
 v[i,0]*=1+.07*math.exp(-((z-1.94)/.065)**2)
bodyverts=[v[i].tolist() for i in used];bodyfaces=[[remap[i] for i in f] for f in faces]
M={}
def mat(name,c,metal=0,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True
 nt=m.node_tree;p=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not p:
  p=nt.nodes.new('ShaderNodeBsdfPrincipled');o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(p.outputs['BSDF'],o.inputs['Surface'])
 p.inputs['Base Color'].default_value=(*[x**2.2 for x in c],1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 m.diffuse_color=(*[x**2.2 for x in c],1);M[name]=m;return m
skin=mat('Weathered skin · 2K albedo',(.66,.45,.34),0,.65)
leather=mat('Oiled oxhide',(.16,.095,.052),0,.86)
edge=mat('Leather cut edges',(.40,.26,.13),0,.85)
steel=mat('Hammered blue steel',(.25,.29,.30),.65,.53)
silver=mat('Honed edge',(.66,.69,.67),.9,.23)
bronze=mat('Old brass',(.40,.28,.14),.6,.57)
cloth=mat('Charcoal wool',(.115,.135,.14),0,.95)
hair=mat('Chestnut hair',(.10,.068,.048),0,.85)
hairlight=mat('Hair highlights',(.24,.16,.105),0,.82)
fur=mat('Wolf underfur',(.255,.265,.23),0,1)
fur_light=mat('Wolf guard hairs',(.46,.44,.36),0,1)
paint=mat('Faded woad',(.08,.17,.21),0,.86)
eye_mat=mat('Ivory sclera',(.7,.64,.54),0,.26)
iris_mat=mat('Grey blue iris',(.15,.29,.31),0,.25)
black=mat('Pupil',(.015,.018,.017),0,.16)
# A tiled micro-normal map survives glTF export, unlike procedural shader nodes.
N=512; yy,xx=np.mgrid[:N,:N];rng=np.random.default_rng(2)
height=rng.normal(0,.14,(N,N))+.13*np.sin(xx*.51)*np.cos(yy*.39)
dy,dx=np.gradient(height);normal=np.dstack((-dx,-dy,np.ones_like(dx)));normal/=np.linalg.norm(normal,axis=2)[:,:,None]
a=np.dstack((normal*.5+.5,np.ones((N,N)))).astype('float32')
im=bpy.data.images.new('Leather grain normal',width=N,height=N);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(a.ravel());im.filepath_raw=str(ROOT/'game/assets/textures/hero_grain_normal.png');im.file_format='PNG';im.save();im.pack()
for m in [leather,cloth,steel,bronze,skin]:
 nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');t=nt.nodes.new('ShaderNodeTexImage');t.image=im
 n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.07 if m==skin else .26;nt.links.new(t.outputs['Color'],n.inputs['Color']);nt.links.new(n.outputs['Normal'],p.inputs['Normal'])
skinpath=REF/'system/skins/middleage_caucasian_male/middleage_lightskinned_male_diffuse.png'
if not skinpath.exists():
 candidates=list((REF/'system').rglob('*caucasian_male*diffuse.png')) if (REF/'system').exists() else []
 if candidates:skinpath=candidates[0]
if skinpath.exists():
 im=bpy.data.images.load(str(skinpath));im.scale(2048,2048);im.pack();nt=skin.node_tree;t=nt.nodes.new('ShaderNodeTexImage');t.image=im;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.69,.59,.49,1);nt.links.new(t.outputs['Color'],mix.inputs[1]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
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
# Fit clothing to the body mesh and transfer its existing weights.
for name,lo,hi,m,offset in [('Wool trousers',.27,1.20,cloth,.014),('Fitted leather boots',0,.54,leather,.022)]:
 chosen=[(f,fu) for f,fu in zip(faces,face_uv) if all(lo<=v[i][2]<=hi for i in f)]
 ids=sorted(set(i for f,_ in chosen for i in f));rm={old:new for new,old in enumerate(ids)}
 vs=[]
 for i in ids:
  idx=remap[i];n=body.data.vertices[idx].normal;vs.append(tuple(Vector(v[i])+n*offset))
 o=mesh(name,vs,[[rm[i] for i in f] for f,_ in chosen],m);uv=o.data.uv_layers.new()
 for p,(_,fu) in zip(o.data.polygons,chosen):
  for li,t in zip(p.loop_indices,fu):uv.data[li].uv=texcoords[t]
 skin_bind(o,ids);s=o.modifiers.new('Fitted silhouette','SUBSURF');s.levels=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_move_up(modifier=s.name)
# Kilt: individual overlapping, stitched leather tassets over the trousers.
for i in range(16):
 a=i*math.tau/16;pts=[]
 for z,rx,ry in [(1.185,.285,.22),(.88+(.035 if i%2 else 0),.34,.24)]:
  for k in range(4):
   ang=a+(k/3-.5)*math.tau/14;pts.append((math.cos(ang)*rx,math.sin(ang)*ry+.028,z))
 o=rigid(mesh('Overlapping leather tasset',pts,[(0,1,5,4),(1,2,6,5),(2,3,7,6)],leather),'spine05');sol=o.modifiers.new('Leather thickness','SOLIDIFY');sol.thickness=.01
 for k in [0,3]:tube('Raised stitched tasset edge',[pts[k],pts[k+4]],[.004,.004],edge,'spine05',5)
 for z in [1.13,1.165]:sphere('Brass tasset rivet',(math.cos(a)*.272,math.sin(a)*.202+.028,z),(.012,.012,.012),bronze,'spine05',8,6)
# Wide belt and metal buckle.
for z in [1.18,1.195,1.21,1.225,1.24]:ring('Layered waist belt',(0,.025,z),.275,.218,.012,leather)
for z in [1.173,1.245]:ring('Belt welt',(0,.025,z),.277,.22,.004,edge)
cube('Iron belt buckle',(0,-.204,1.209),(.16,.028,.108),bronze,'spine05',.012)
cube('Buckle inset',(0,-.224,1.21),(.122,.016,.077),steel,'spine05',.009)
for s in [-1,1]:tube('Wolf sigil',[(s*.045,-.237,1.24),(s*.02,-.238,1.21),(0,-.24,1.18)],[.008]*3,silver,'spine05')
from mathutils.kdtree import KDTree
kd=KDTree(len(used))
for idx,old in enumerate(used):kd.insert(Vector(v[old]),old)
kd.balance()
vertexweights={}
for bone,entries in weights.items():
 for idx,w in entries:vertexweights.setdefault(idx,[]).append((bone,w))
def fitted(o):
 fit_uv(o)
 for vert in o.data.vertices:
  _,idx,_=kd.find(vert.co)
  for bone,w in vertexweights.get(idx,[]):
   g=o.vertex_groups.get(bone) or o.vertex_groups.new(name=bone);g.add([vert.index],w,'REPLACE')
 mod=o.modifiers.new('Fitted skin deformation','ARMATURE');mod.object=rig;o.parent=rig
 return o
# Diagonal harness raycast to the real torso. The strap follows pectoral curvature.
for back in [False,True]:
 vs=[]
 for k in range(29):
  t=k/28;x=-.25+t*.45;z=1.73-t*.44
  for side in [-1,1]:
   xx=x+side*.042;origin=Vector((xx,1 if back else -1,z));direction=Vector((0,-1 if back else 1,0));hit=bvh.ray_cast(origin,direction)
   y=hit[0].y+(.013 if back else -.013) if hit[0] else (.18 if back else -.18)
   vs.append((xx,y,z))
 fs=[(k*2,k*2+1,k*2+3,k*2+2) for k in range(28)]
 o=fitted(mesh('Cross chest baldric',vs,fs,leather));sol=o.modifiers.new('Harness thickness','SOLIDIFY');sol.thickness=.01
 for side in [0,1]:
  seam=tube('Harness stitch seam',vs[side::2],[.0025]*29,edge,'spine02',5)
  seam.vertex_groups.clear();seam.modifiers.clear();fitted(seam)
 if not back:
  for k in [7,8,9]:
   a=Vector(vs[k*2]);b=Vector(vs[k*2+1]);tube('Harness brass buckle',[a+Vector((0,-.01,0)),b+Vector((0,-.01,0))],[.006]*2,bronze,'spine02')
# Shoulder armor as shaped shell plates, not a scaled ball.
for sign,side in [(1,'L'),(-1,'R')]:
 shoulder=joint('upperarm01.'+side+'____head');bn='upperarm01.'+side
 if sign==1:
  for layer in range(3):
   vs=[]
   for row in range(7):
    th=.22+row/6*1.20
    for k in range(13):
     a=-math.pi+k/12*math.pi;vs.append(tuple(shoulder+Vector((sign*(math.sin(th)*(.18+layer*.018)+layer*.047),math.cos(a)*.195*math.cos(th*.3),.14*math.cos(th)+math.sin(a)*.095-layer*.022))))
   o=rigid(mesh('Laminated iron pauldron',vs,[(r*13+k,r*13+k+1,(r+1)*13+k+1,(r+1)*13+k) for r in range(6) for k in range(12)],steel),bn)
   sol=o.modifiers.new('Plate thickness','SOLIDIFY');sol.thickness=.012
   tube('Pauldron bronze rim',vs[-13:],[.007]*13,bronze,bn)
   for k in [1,4,8,11]:sphere('Pauldron rivet',Vector(vs[-13+k])+Vector((0,-.009,0)),(.012,.009,.012),bronze,bn,8,6)
 # Bracers with elliptical rings aligned to the actual forearm.
 elbow=joint('lowerarm01.'+side+'____head');wrist=joint('wrist.'+side+'____head');direction=(wrist-elbow).normalized();q=direction.to_track_quat('Z','Y')
 for j in range(8):
  t=.40+j*.067;c=elbow.lerp(wrist,t);r=.105-t*.035
  pts=[c+q@Vector((r*math.cos(k*math.tau/32),r*math.sin(k*math.tau/32),0)) for k in range(33)]
  tube('Wrapped vambrace',pts,[.013]*33,leather if j%3 else bronze,'lowerarm01.'+side)
 # Construct a leather toe box and stitched sole, hiding individual toes.
 points=[p for p in bodyverts if p[2]<.17 and p[0]*sign>0]
 xs=[p[0] for p in points];ys=[p[1] for p in points]
 foot=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,0))
 width=max(xs)-min(xs)+.035;depth=max(ys)-min(ys)+.045
 cube('Reinforced boot toe',(foot.x,foot.y,.11),(width,depth,.21),leather,'foot.'+side,.07)
 cube('Thick boot sole',(foot.x,foot.y,.034),(width+.008,depth+.008,.06),edge,'foot.'+side,.026)
 # Shin armor, three layers and external boot straps.
 knee=joint('lowerleg01.'+side+'____head');ankle=joint('foot.'+side+'____head')
 for z in [.19,.31,.43]:
  t=(z-ankle.z)/(knee.z-ankle.z);c=ankle.lerp(knee,max(0,t));ring('Boot strap',(c.x,c.y,z),.082,.088,.012,leather,'lowerleg01.'+side)
 for k in range(3):
  z=.22+k*.075;c=ankle.lerp(knee,(z-ankle.z)/(knee.z-ankle.z));cube('Forged shin plate',(c.x,c.y-.091,z),(.127,.025,.085),steel,'lowerleg01.'+side,.018)
 # Axe and offhand sword are weighted to the wrist bone, following the grip.
 hand=joint('wrist.'+side+'____tail');p=hand+Vector((0,-.024,0));bn='wrist.'+side
 tube('Weapon grip',[p+Vector((0,0,-.13)),p+Vector((0,0,.17))],[.025,.022],leather,bn,12)
 for k in range(8):ring('Grip binding',p+Vector((0,0,-.12+k*.034)),.026,.026,.004,edge,bn)
 if sign==-1:
  tube('Ash axe haft',[p+Vector((0,0,-.26)),p+Vector((0,0,.62))],[.022,.02],edge,bn,12)
  profile=[(-.015,.52),(.12,.63),(.28,.69),(.35,.61),(.36,.38),(.30,.26),(.18,.31),(.09,.43),(-.015,.43)]
  vs=[tuple(p+Vector((x,y,z))) for y in [-.025,.025] for x,z in profile];n=len(profile);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  o=rigid(mesh('Bearded battle axe',vs,fs,steel),bn);mod=o.modifiers.new('Forged bevel','BEVEL');mod.width=.009;mod.segments=3
  tube('Honed axe cutting edge',[p+Vector((x,-.029,z)) for x,z in profile[2:7]],[.009]*5,silver,bn)
  for k in range(5):tube('Chisel marks on axe',[p+Vector((.12+k*.026,-.03,.50)),p+Vector((.14+k*.026,-.03,.53))],[.0025]*2,bronze,bn,4)
 else:
  tube('Sword crossguard',[p+Vector((-.13,0,.19)),p+Vector((.13,0,.19))],[.018,.018],bronze,bn,8)
  vs=[tuple(p+Vector(x)) for x in [(-.037,0,.2),(0,-.018,.2),(.037,0,.2),(0,.018,.2),(-.025,0,.75),(0,-.013,.75),(.025,0,.75),(0,.013,.75),(0,0,.91)]]
  rigid(mesh('Tempered offhand sword',vs,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,8),(5,6,8),(6,7,8),(7,4,8)],silver),bn)
 sphere('Weapon pommel',p+Vector((0,0,-.15)),(.032,.032,.037),bronze,bn,12,8)
# Back-mounted two handed arsenal, with a readable sword silhouette.
p=Vector((-.28,.205,1.07));tip=Vector((.37,.22,2.17));d=(tip-p).normalized();side=Vector((d.z,0,-d.x))
tube('Back scabbard',[p,tip-d*.28],[.046,.046],leather,'spine02',8)
tube('Back sword hilt',[tip-d*.27,tip],[.025,.025],edge,'spine02',10)
tube('Greatsword crossguard',[tip-d*.27-side*.17,tip-d*.27+side*.17],[.019,.019],steel,'spine02')
sphere('Greatsword pommel',tip,(.04,.03,.04),bronze,'spine02')
# Fur mantle: tapered grouped fibers along the back and shoulders.
for i in range(300):
 x=random.uniform(-.38,.38);y=random.uniform(.08,.19);z=1.73+(.05*(1-abs(x)/.4))+random.uniform(-.02,.03)
 p=Vector((x,y,z));length=random.uniform(.055,.14);pts=[p,p+Vector((x*.10,.025,-length*.4)),p+Vector((x*.18,.06,-length))]
 tube('Wolf fur tuft',pts,[.015,.012,.001],fur if i%3 else fur_light,'spine01',4)
# Actual eyes fitted to locator centers; the iris sits within the eyelids.
for side in ['L','R']:
 c=joint('eye.'+side+'____head');sphere('Eyeball '+side,c,(.022,.022,.022),eye_mat,'head',24,16)
 sphere('Iris '+side,c+Vector((0,-.019,0)),(.010,.006,.010),iris_mat,'head',20,10)
 sphere('Pupil '+side,c+Vector((0,-.024,0)),(.004,.002,.005),black,'head',16,8)
# Short eyebrows, with brows angled into a stern expression.
for sign,side in [(1,'L'),(-1,'R')]:
 c=joint('eye.'+side+'____head')
 for i in range(70):
  t=random.random();x=c.x+sign*(t-.45)*.047;z=c.z+.025+.009*(1-t)+random.uniform(-.002,.002)
  hit=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
  if hit[0]:
   p=hit[0]+Vector((0,-.002,0));tube('Angled eyebrow',[p,p+Vector((sign*.006,-.001,.003))],[.0013,.0001],hair,'head',4)
# A thin healed cheek scar follows the facial surface.
scar=mat('Healed scar tissue',(.51,.32,.25),0,.75)
vs=[]
for k in range(15):
 x=-.068+k*.002;z=2.01-k*.004
 for sign in [-1,1]:
  xx=x+sign*.0017;hit=bvh.ray_cast(Vector((xx,-1,z)),Vector((0,1,0)))
  if hit[0]:vs.append(tuple(hit[0]+Vector((0,-.0017,0))))
if len(vs)==30:rigid(mesh('Old cheek scar',vs,[(k*2,k*2+1,k*2+3,k*2+2) for k in range(14)],scar),'head')
# Shaved crown with long swept central locks. Curves become one skinned mesh.
head=joint('head____head');crown=max(p[2] for p in bodyverts)
for i in range(400):
 x=random.uniform(-.085,.085);y=random.uniform(-.075,.14);r=max(0,1-(x/.145)**2-((y-.02)/.18)**2);z=crown-.035+(math.sqrt(r)-1)*.07
 p=Vector((x,y,z));pts=[p,p+Vector((random.uniform(-.01,.01),.06,.026)),p+Vector((x*.12,.15,-.01)),p+Vector((x*.2,.20,-.10-random.random()*.04))]
 tube('Swept hair strand',pts,[.003,.004,.002,.0002],hair if i%4 else hairlight,'head',5)
# Beard follows the lower face, with individually tapered strands and bound plaits.
for i in range(550):
 x=random.uniform(-.083,.083);z=random.uniform(crown-.28,crown-.18)
 hit=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
 if not hit[0]:continue
 p=hit[0]+Vector((0,-.004,0));length=random.uniform(.03,.08)*(1.2-abs(x)*5)
 tube('Beard fibers',[p,p+Vector((x*.05,-.013,-length*.45)),p+Vector((x*.13,-.018,-length))],[.002,.0026,.0002],hair if i%5 else hairlight,'head',4)
for sign in [-1,1]:
 x=sign*.026;z=crown-.278;hit=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
 if hit[0]:
  p=hit[0]+Vector((0,-.012,-.008))
  for strand in range(3):
   pts=[p+Vector((math.sin(k*.9+strand*math.tau/3)*.007,math.cos(k*.9+strand*math.tau/3)*.007,-k*.008)) for k in range(14)]
   tube('Bound beard braid',pts,[.006*(1-k/17) for k in range(14)],hairlight,'head',5)
  ring('Beard bronze clasp',p+Vector((0,0,-.075)),.01,.01,.005,bronze,'head')
# Small, irregular war paint ribbons conformed to the forehead and torso.
for xbase,z0,length,width,bone in [(-.052,crown-.035,.17,.012,'head'),(.052,crown-.04,.16,.008,'head'),(-.15,1.65,.20,.012,'spine02')]:
 vs=[]
 for k in range(18):
  z=z0-k/17*length;x=xbase+.014*math.sin(k*.13)
  for sign in [-1,1]:
   xx=x+sign*width*(.9+.1*math.sin(k*2));hit=bvh.ray_cast(Vector((xx,-1,z)),Vector((0,1,0)));vs.append((xx,(hit[0].y if hit[0] else -.13)-.002,z))
 rigid(mesh('Woad battle marking',vs,[(k*2,k*2+1,k*2+3,k*2+2) for k in range(17)],paint),bone)
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
# Authored local clips, built from world-axis rotations in the anatomical rest space.
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
def rot(name,axis,angle):
 pb=rig.pose.bones.get(name)
 if not pb:return
 q=pb.bone.matrix_local.to_quaternion();pb.rotation_quaternion=pb.rotation_quaternion @ (q.inverted()@Quaternion(Vector(axis),angle)@q)
def pose(kind,t):
 for pb in rig.pose.bones:pb.rotation_quaternion=Quaternion();pb.location=(0,0,0)
 # Lower A-pose arms into a compact, heavy combat stance.
 for side,sign in [('L',1),('R',-1)]:
  rot('upperarm01.'+side,(0,1,0),sign*.42)
  rot('lowerarm01.'+side,(1,0,0),-.20)
  for finger in range(2,6):
   for part in range(1,4):rot(f'finger{finger}-{part}.{side}',(1,0,0),-.8)
  rot('finger1-2.'+side,(0,0,1),sign*.35)
 rot('spine02',(1,0,0),.025)
 if kind in ['Idle','Run']:
  rig.pose.bones['root'].location.z=.007*math.sin(t*math.tau)
  rot('spine01',(1,0,0),.01*math.sin(t*math.tau))
 if kind=='Run':
  for side,sign in [('L',1),('R',-1)]:
   wave=math.sin(t*math.tau)*sign
   rot('upperleg01.'+side,(1,0,0),wave*.48);rot('lowerleg01.'+side,(1,0,0),max(0,-wave)*.67)
   rot('upperarm01.'+side,(1,0,0),-wave*.36)
  rig.pose.bones['root'].location.z=.02+abs(math.sin(t*math.tau))*.032
  rot('spine03',(1,0,0),.10)
 if kind=='Attack':
  wind=math.sin(min(t/.43,1)*math.pi/2) if t<.43 else max(0,1-(t-.43)/.35)
  rot('upperarm01.R',(1,0,0),-wind*1.75);rot('upperarm01.R',(0,0,1),-.28*wind)
  rot('spine02',(0,0,1),-.32*math.sin(t*math.tau));rot('upperarm01.L',(1,0,0),-wind*.35)
 if kind=='Whirlwind':
  for side,sign in [('L',1),('R',-1)]:
   rot('upperarm01.'+side,(0,1,0),-sign*1.22);rot('lowerarm01.'+side,(1,0,0),.10)
   rot('upperleg01.'+side,(1,0,0),math.sin(t*math.tau)*sign*.23)
 if kind in ['Shout','Berserk']:
  f=math.sin(t*math.pi)
  for side,sign in [('L',1),('R',-1)]:rot('upperarm01.'+side,(0,1,0),-sign*f*.55);rot('upperarm01.'+side,(1,0,0),-f*.8)
  rot('spine03',(1,0,0),-.17*f);rot('head',(1,0,0),-.10*f)
 if kind=='Leap':
  f=math.sin(t*math.pi)
  for side,sign in [('L',1),('R',-1)]:
   rot('upperarm01.'+side,(1,0,0),-f*2.2);rot('upperleg01.'+side,(1,0,0),f*.65);rot('lowerleg01.'+side,(1,0,0),-f*.9)
 if kind=='Death':
  f=min(1,t*1.5);rot('root',(1,0,0),-f*1.48);rig.pose.bones['root'].location.z=-.88*f
clips=[('Idle',2.4),('Run',.72),('Attack',.72),('Whirlwind',.60),('Shout',.7),('Berserk',.9),('Leap',.8),('Death',1.2)]
rig.animation_data_create();bpy.context.scene.render.fps=30
for name,duration in clips:
 action=bpy.data.actions.new(name);rig.animation_data.action=action;frames=round(duration*30)
 for frame in range(frames+1):
  pose(name,frame/frames)
  for pb in rig.pose.bones:
   pb.keyframe_insert('rotation_quaternion',frame=frame+1,group=pb.name)
   if pb.name=='root':pb.keyframe_insert('location',frame=frame+1,group=pb.name)
 action.use_fake_user=True
 track=rig.animation_data.nla_tracks.new();track.name=name;strip=track.strips.new(name,1,action);track.mute=True
rig.animation_data.action=None;pose('Idle',0);bpy.context.scene.frame_set(1)
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
 if m['name'].startswith('Weathered skin'):m['pbrMetallicRoughness']['baseColorFactor']=[.69,.59,.49,1]
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
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/barbarian.blend'))
print('HERO meshes',len([o for o in scene.objects if o.type=='MESH']),'triangles',sum(len(o.data.polygons)*2 for o in scene.objects if o.type=='MESH'),'bones',len(rig.data.bones),flush=True)
bpy.ops.render.render(write_still=True)
print('ASHEN OATH: anatomical barbarian exported and portrait rendered.')
